"""Check PyBullet with a falling cube; no robot model or GUI required."""
from importlib.metadata import version


def run_check():
    import pybullet as p
    import pybullet_data

    client = p.connect(p.DIRECT)
    if client < 0:
        raise RuntimeError('Cannot connect to PyBullet')
    try:
        p.setAdditionalSearchPath(pybullet_data.getDataPath(), physicsClientId=client)
        p.setGravity(0, 0, -9.81, physicsClientId=client)
        p.setTimeStep(1 / 240, physicsClientId=client)
        p.loadURDF('plane.urdf', physicsClientId=client)
        cube = p.loadURDF('cube_small.urdf', [0, 0, 1], physicsClientId=client)
        for _ in range(480):
            p.stepSimulation(physicsClientId=client)
        height = p.getBasePositionAndOrientation(cube, physicsClientId=client)[0][2]
        if not 0 < height < 0.1:
            raise RuntimeError(f'Unexpected final cube height: {height}')
        return f'pybullet {version("pybullet")}; 480 steps; final height={height:.6f} m'
    finally:
        p.disconnect(client)


if __name__ == '__main__':
    print(run_check())
