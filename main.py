import numpy as np
import magpylib as magpy


def create_coil(radius_cm: float = 5.5, length_cm: float = 40, angle_deg: float = 60, current_A: float = 100):

    # coil spans in: (0 - angle_deg, 0 + angle_deg) and (180 - angle_deg, 180 + angle_deg)
    arc_num = 100

    radius_mm = 10 * radius_cm
    length_mm = 10 * length_cm

    saddle_coil = magpy.Collection()

    wire_at_center = magpy.current.Line(
        current=current_A,
        vertices=(
            (0, 0, -length_mm / 2.),
            (0, 0, length_mm / 2.),
        ),
    )
    arc_vertices = tuple((radius_mm * np.cos(np.deg2rad(this_angle_deg)), radius_mm * np.sin(np.deg2rad(this_angle_deg)), 0)
                         for this_angle_deg in np.linspace(start=0 - angle_deg, stop=0 + angle_deg, num=arc_num, endpoint=True))
    arc_at_center = magpy.current.Line(current=current_A, vertices=arc_vertices)

    wire_up_move = (radius_mm * np.cos(np.deg2rad(-angle_deg)), radius_mm * np.sin(np.deg2rad(-angle_deg)), 0)
    wire_1_up = wire_at_center.copy().move(displacement=wire_up_move)
    wire_1_down = wire_1_up.copy().rotate_from_angax(angle=180., axis='y').rotate_from_angax(angle=2*angle_deg, axis='z', anchor=0)
    arc_1_up = arc_at_center.copy().move(displacement=(0, 0, length_mm / 2.))
    arc_1_down = arc_at_center.copy().rotate_from_angax(angle=180., axis='x').move(displacement=(0, 0, -length_mm / 2.))

    wire_2_down = wire_1_up.copy().rotate_from_angax(angle=180, axis='z', anchor=0).rotate_from_angax(angle=180, axis='x')
    wire_2_up = wire_1_down.copy().rotate_from_angax(angle=180, axis='z', anchor=0).rotate_from_angax(angle=180, axis='x')
    arc_2_up = arc_1_up.copy().rotate_from_angax(angle=180, axis='z', anchor=0).rotate_from_angax(angle=180, axis='x')
    arc_2_down = arc_1_down.copy().rotate_from_angax(angle=180, axis='z', anchor=0).rotate_from_angax(angle=180, axis='x')

    saddle_coil.add(wire_1_up)
    saddle_coil.add(arc_1_up)
    saddle_coil.add(wire_1_down)
    saddle_coil.add(arc_1_down)

    saddle_coil.add(wire_2_up)
    saddle_coil.add(arc_2_up)
    saddle_coil.add(wire_2_down)
    saddle_coil.add(arc_2_down)

    return saddle_coil


def plot_field_xz_plane(coil, radius_cm: float = 5.5, length_cm: float = 40):
    # create grid
    xs = np.linspace(start=-2 * 10 * radius_cm, stop=2 * 10 * radius_cm, num=10)
    zs = np.linspace(start=-1.5 * 10 * length_cm / 2, stop=1.5 * 10 * length_cm / 2, num=10)

    grid = np.array([[(x, 0, z) for x in xs] for z in zs])

    # compute and plot field
    B = magpy.getB(saddle_coil, grid)
    Bamp = np.linalg.norm(B, axis=2)
    Bamp /= np.amax(Bamp)

    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 1, figsize=(13, 5))

    sp = ax.streamplot(
        grid[:, :, 0],
        grid[:, :, 2],
        B[:, :, 0],
        B[:, :, 2],
        density=2,
        color=Bamp,
        linewidth=1,
        cmap='coolwarm',
    )

    # figure styling
    ax.set(
        title='Magnetic field of coil1',
        xlabel='x-position [mm]',
        ylabel='z-position [mm]',
        aspect=1
    )

    plt.colorbar(sp.lines, ax=ax, label='[mT]')
    plt.tight_layout()
    plt.show()


def plot_field_z_axis(coil, radius_cm: float = 5.5, length_cm: float = 40):
    # create grid
    zs = np.linspace(start=-1.5 * 10 * length_cm / 2, stop=1.5 * 10 * length_cm / 2, num=1000)

    grid = np.array([(0, 0, z) for z in zs])

    # compute and plot field
    B = magpy.getB(saddle_coil, grid)

    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 1, figsize=(13, 5))

    print(B.shape)

    sp = ax.plot(zs, B[:, 0], label='Bx')
    sp = ax.plot(zs, B[:, 1], label='By')
    sp = ax.plot(zs, B[:, 2], label='Bz')

    # figure styling
    ax.set(
        title='Magnetic field',
        xlabel='z-position [mm]',
        ylabel='B [mT]',
    )
    ax.grid()
    plt.legend()
    plt.tight_layout()
    plt.show()


def save_field(coil, filename: str = 'field.csv'):
    # create grid
    zs = np.linspace(start=-1.5 * 10 * length_cm / 2, stop=1.5 * 10 * length_cm / 2, num=100)

    grid = np.array([(0, 0, z) for z in zs])

    # compute and plot field
    df = magpy.getB(saddle_coil, grid, output='dataframe')
    df.to_csv(filename)



if __name__ == '__main__':

    length_cm = 40
    radius_cm = 5.5
    saddle_coil = create_coil(length_cm=length_cm, radius_cm=radius_cm)
    #saddle_coil.show()

    #plot_field_z_axis(saddle_coil, length_cm=length_cm, radius_cm=radius_cm)
    #plot_field_xz_plane(saddle_coil, length_cm=length_cm, radius_cm=radius_cm)
    save_field(saddle_coil)