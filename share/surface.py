import ase.io, os
from utilities import relax_config, model_test_root, run_root, rescale_to_relaxed_bulk, evaluate
import numpy as np

# the current 
import model 

def do_symmetric_surface(test_dir):
    surf = ase.io.read(test_dir+"/surface.xyz", format="extxyz")

    bulk = rescale_to_relaxed_bulk(surf)
    bulk_Zs = bulk.get_atomic_numbers()
    evaluate(bulk)
    bulk_cell = bulk.get_cell()
    bulk_E = bulk.get_potential_energy()

    try:
        model.reset_config()
    except AttributeError:
        pass

    print("got relaxed bulk cell ", bulk_cell)
    print("got rescaled surf cell ", surf.get_cell())

    # relax surface system
    tol = 1.0e-2
    surf = relax_config(surf, relax_pos=True, relax_cell=False, tol=tol, traj_file=None, config_label="surface", from_base_model=True, save_config=True)

    ase.io.write(os.path.join("..",run_root+"-relaxed.xyz"),  surf, format='extxyz')

    # check stoichiometry and number of bulk cell energies to subtract
    surf_Zs = surf.get_atomic_numbers()
    Z0 = bulk_Zs[0]
    n_bulk_cells = float(sum(surf_Zs == Z0))/float(sum(bulk_Zs == Z0))
    if len(set(bulk_Zs)) == 1:
        n_dmu = None
    else:
        n_dmu = {}
        for Z in set(bulk_Zs):
            n_dmu[Z] = n_bulk_cells*sum(bulk_Zs == Z) - sum(surf_Zs == Z)

    # calculate surface energy
    area = np.linalg.norm(np.cross(surf.get_cell()[0,:],surf.get_cell()[1,:]))

    print("got surface cell potential energy", surf.get_potential_energy())
    print("got bulk potential energy",bulk_E*n_bulk_cells)
    print("got area",area)

    return { "bulk_struct_test" : surf.info["bulk_struct_test"],  "Ef" : (surf.get_potential_energy() - bulk_E*n_bulk_cells)/(2.0*area), "dmu" : n_dmu, 'filename' : run_root+"-relaxed.xyz" }
