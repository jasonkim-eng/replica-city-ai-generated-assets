"""Basic Isaac contact qualification: 3 drop poses/asset + mug cavity probe.

Not a robot-grasp benchmark, friction calibration or formal SimReady certification.
Only a fresh process/stage and this task's output directory are modified.
"""
import argparse
import hashlib
import json
from pathlib import Path
import time

parser=argparse.ArgumentParser()
parser.add_argument('--assets',type=Path,required=True)
parser.add_argument('--out',type=Path,required=True)
parser.add_argument('--physics-hz',type=int,default=480)
args=parser.parse_args()
if args.physics_hz<60:parser.error('physics-hz must be at least 60')
dt=1/args.physics_hz;steps=6*args.physics_hz
args.assets=args.assets.resolve();args.out=args.out.resolve();args.out.mkdir(parents=True,exist_ok=True)
started=time.monotonic()
source_sha256={str(p.relative_to(args.assets)):hashlib.sha256(p.read_bytes()).hexdigest()
               for p in sorted(args.assets.rglob('*.usd*'))}

from isaacsim import SimulationApp
app=SimulationApp({'headless':True,'width':1280,'height':900,'anti_aliasing':0})
exit_code=1
try:
    import numpy as np
    import omni.physx
    from pxr import Usd,UsdGeom,UsdPhysics,UsdShade,UsdLux,Sdf,Gf,PhysxSchema
    from isaacsim.core.api import World
    from isaacsim.core.api.objects import FixedCuboid
    from isaacsim.core.prims import RigidPrim
    from isaacsim.core.utils.stage import add_reference_to_stage
    from isaacsim.core.utils.viewports import set_camera_view

    ids=['wood_block_001','food_carton_001','food_can_001','ceramic_mug_001','cell_phone_001']
    world=World(stage_units_in_meters=1.,physics_dt=dt,rendering_dt=1/60)
    world.scene.add(FixedCuboid(prim_path='/World/Floor',name='floor',
        position=np.array([0.,0.,-.025]),scale=np.array([3.,3.,.05]),color=np.array([.28,.32,.36])))
    stage=world.stage
    records=[];paths=[]
    def local_visual_points(asset_id):
        source=Usd.Stage.Open(str(args.assets/asset_id/(asset_id+'.usda')))
        cache=UsdGeom.XformCache();pts=[]
        for prim in source.Traverse():
            if prim.IsA(UsdGeom.Mesh) and '/visuals/' in str(prim.GetPath()):
                matrix=cache.GetLocalToWorldTransform(prim)
                pts.extend(tuple(matrix.Transform(Gf.Vec3d(p))) for p in UsdGeom.Mesh(prim).GetPointsAttr().Get())
        return np.array(pts,dtype=float)
    pose_rots=[Gf.Rotation(Gf.Vec3d(1,0,0),0),
               Gf.Rotation(Gf.Vec3d(1,0,0),17)*Gf.Rotation(Gf.Vec3d(0,1,0),23),
               Gf.Rotation(Gf.Vec3d(1,0,0),90)]
    for j,name in enumerate(ids):
        pts=local_visual_points(name)
        for k,rotation in enumerate(pose_rots):
            path='/World/test_%d_%d'%(j,k)
            add_reference_to_stage(str(args.assets/name/(name+'_isaac.usda')),path)
            quat=rotation.GetQuat();matrix=np.array(Gf.Matrix3d(quat))
            bottom=float((pts@matrix)[:,2].min())
            position=[(j-2)*.26,(k-1)*.32,.05-bottom]
            xf=UsdGeom.Xformable(stage.GetPrimAtPath(path));xf.ClearXformOpOrder()
            xf.AddTranslateOp().Set(Gf.Vec3d(*position));xf.AddOrientOp().Set(Gf.Quatf(quat))
            records.append({'asset_id':name,'pose':k,'path':path,'points':pts,'initial_position':position})
            paths.append(path)
    # Independent kinematic mug fixture for cavity/open-handle checks.
    fixture_path='/World/cavity_mug'
    add_reference_to_stage(str(args.assets/'ceramic_mug_001/ceramic_mug_001_isaac.usda'),fixture_path)
    fixture=stage.GetPrimAtPath(fixture_path)
    UsdPhysics.RigidBodyAPI(fixture).CreateKinematicEnabledAttr(True)
    UsdGeom.Xformable(fixture).AddTranslateOp().Set(Gf.Vec3d(.85,0,0))
    ball=UsdGeom.Sphere.Define(stage,'/World/cavity_probe');ball.CreateRadiusAttr(.005)
    ball.CreateDisplayColorAttr([Gf.Vec3f(.9,.1,.1)])
    UsdGeom.Xformable(ball).AddTranslateOp().Set(Gf.Vec3d(.85,0,.15))
    UsdPhysics.RigidBodyAPI.Apply(ball.GetPrim());UsdPhysics.CollisionAPI.Apply(ball.GetPrim())
    UsdPhysics.MassAPI.Apply(ball.GetPrim()).CreateMassAttr(.002)
    paths.append('/World/cavity_probe')
    # One filter list per explicit body path; an empty flat list is not valid for
    # multiple sensor patterns in the installed Isaac 6 contact-view API.
    body=world.scene.add(RigidPrim(paths,name='drop_bodies',track_contact_forces=True,
                                  contact_filter_prim_paths_expr=[['/World/Floor'] for _ in paths],
                                  disable_stablization=False,
                                  prepare_contact_sensors=True,max_contact_count=8192))
    # Asset settings come directly from the delivered profile, not test overrides.
    # Use matching contact precision for the test floor/probe only.
    for prim in stage.Traverse():
        if str(prim.GetPath()) not in ('/World/Floor','/World/cavity_probe'):
            continue
        if prim.HasAPI(UsdPhysics.CollisionAPI):
            api=PhysxSchema.PhysxCollisionAPI.Apply(prim)
            api.CreateContactOffsetAttr(.001);api.CreateRestOffsetAttr(0.)
        if prim.HasAPI(UsdPhysics.RigidBodyAPI):
            api=PhysxSchema.PhysxRigidBodyAPI.Apply(prim)
            api.CreateSolverPositionIterationCountAttr(16)
            api.CreateSolverVelocityIterationCountAttr(4)
    UsdLux.DomeLight.Define(stage,'/World/Dome').CreateIntensityAttr(500)
    light=UsdLux.DistantLight.Define(stage,'/World/Key');light.CreateIntensityAttr(2200)
    UsdGeom.Xformable(light).AddRotateXYZOp().Set(Gf.Vec3f(-35,20,15))
    set_camera_view(eye=np.array([1.15,-1.55,1.25]),target=np.array([.1,0,.02]))
    stage.GetRootLayer().Export(str(args.out/'validation_initial.usda'))
    world.reset()
    initial_positions,initial_quats=body.get_world_poses()
    print('ISAAC_TEST_INITIALIZED',len(paths),'bodies',flush=True)
    traces=[];last=[];forces=[]
    for step in range(steps):
        world.step(render=False)
        if step%12==0:
            positions,quats=body.get_world_poses()
            traces.append({'time_s':(step+1)*dt,'positions':positions.tolist(),'quaternions_wxyz':quats.tolist()})
            if step>=5*args.physics_hz:
                last.append(np.array(positions,copy=True))
                forces.append(np.array(body.get_net_contact_forces(dt=dt),copy=True))
        if (step+1)%(2*args.physics_hz)==0:print('ISAAC_TEST_STEP',step+1,flush=True)
    positions,quats=body.get_world_poses()
    linear=body.get_linear_velocities();angular=body.get_angular_velocities()
    tail=np.array(last);results=[]
    mean_forces=np.mean(forces,axis=0) if forces else None
    for i,record in enumerate(records):
        q=quats[i];rotation=np.array(Gf.Matrix3d(Gf.Quatd(float(q[0]),Gf.Vec3d(*map(float,q[1:])))))
        transformed=record['points']@rotation+positions[i]
        bottom=float(transformed[:,2].min());motion=float(np.linalg.norm(np.ptp(tail[:,i,:],axis=0)))
        speed=float(np.linalg.norm(linear[i]));spin=float(np.linalg.norm(angular[i]))
        checks={'finite':bool(np.isfinite(transformed).all()),'not_fallen_through':bottom>-.002,
                'near_floor':abs(bottom)<.003,'settled_last_second':motion<.0015,
                'low_linear_speed':speed<.01,'low_angular_speed':spin<.1,
                'contact_force_recorded':bool(mean_forces is not None and np.isfinite(mean_forces[i]).all()
                                               and np.linalg.norm(mean_forces[i])>.01),
                'actually_dropped':float(initial_positions[i,2]-positions[i,2])>.015}
        result={k:record[k] for k in ('asset_id','pose','path')}
        result.update(passed=all(checks.values()),checks=checks,bottom_z_m=bottom,
                      last_second_translation_range_m=motion,linear_speed_m_s=speed,
                      angular_speed_rad_s=spin,final_position_m=positions[i].tolist(),
                      final_quaternion_wxyz=quats[i].tolist(),
                      mean_net_contact_force_n=mean_forces[i].tolist() if mean_forces is not None else None)
        results.append(result)
    probe_position=positions[-1]
    query=omni.physx.get_physx_scene_query_interface()
    ray=query.raycast_closest((.906,-.06,.049),(0,1,0),.12)
    cavity={'probe_radius_m':.005,'probe_initial_z_m':.15,'probe_final_position_m':probe_position.tolist(),
            'probe_reached_inner_floor':bool(.008<probe_position[2]<.016 and abs(probe_position[0]-.85)<.025),
            'handle_center_ray_clear':not bool(ray.get('hit',False)),
            'handle_ray_origin_m':[.906,-.06,.049],'handle_ray_direction':[0,1,0],
            'handle_ray_length_m':.12}
    passed=all(r['passed'] for r in results) and cavity['probe_reached_inner_floor'] and cavity['handle_center_ray_clear']
    result={'passed':passed,'isaac_version':'6.0.0.1','physics_dt':dt,'simulated_seconds':6.,
            'drop_height_m':.05,'trials':results,'mug_cavity_test':cavity,
            'physx_profile':{'contact_offset_m':.001,'rest_offset_m':0.,
                             'solver_position_iterations':16,'solver_velocity_iterations':4,
                             'contact_sensor_disables_stabilization':False},
            'entrypoint_suffix':'_isaac.usda','source_usd_sha256':source_sha256,
            'robot_grasp_tested':False,'simready_certified':False,
            'scope':'Drop/rest and mug cavity contact tests only; no robot, calibrated friction, fracture or compliance.',
            'wall_seconds':round(time.monotonic()-started,3)}
    (args.out/'physics_validation.json').write_text(json.dumps(result,indent=2)+'\n')
    (args.out/'drop_traces.json').write_text(json.dumps(traces)+'\n')
    stage.GetRootLayer().Export(str(args.out/'validation_final.usda'))
    print('ISAAC_TEST_RESULT='+json.dumps({'passed':passed,'passed_trials':sum(r['passed'] for r in results),
          'total_trials':len(results),'cavity':cavity}),flush=True)
    # Capture actual USD appearance in the simulator, after all measurements.
    try:
        from omni.kit.viewport.utility import get_active_viewport,capture_viewport_to_file
        for _ in range(45):app.update()
        capture_viewport_to_file(get_active_viewport(),str(args.out/'isaac_validation.png'))
        for _ in range(20):app.update()
    except Exception as error:
        print('SCREENSHOT_WARNING',str(error),flush=True)
    exit_code=0 if passed else 2
except Exception:
    import traceback
    traceback.print_exc()
finally:
    app.close()
raise SystemExit(exit_code)
