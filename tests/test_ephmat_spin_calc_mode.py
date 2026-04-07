import numpy as np
import pytest
import os
import h5py

import perturbopy.postproc as ppy


@pytest.fixture()
def gaas_ephmat_spin():
    """
    Method to generate the EphmatSpinCalcMode object corresponding to GaAs YAML file.

    Returns
    -------
    ephmat_spin : ppy.EphmatSpinCalcMode

    """
    yml_path = os.path.join("refs", "gaas_ephmat_spin.yml")
    return ppy.EphmatSpin.from_yaml(yml_path)

@pytest.mark.parametrize("show_qpoint_labels", [
                        (False), (True)
])
def test_plot_phdisp(gaas_ephmat_spin, plt, show_qpoint_labels, with_plt):
    """
    Method to test EphmatSpin.plot_phdisp function
    
    Method to plot the phonon dispersion.

    Parameters
    ----------
    show_qpoint_labels : bool, optional
        If true, the q-point labels stored in the labels attribute will be shown on the plot. Default true.

    """
    
    if not with_plt:
        pytest.skip("Test requires pytest-plt")

    fig, ax = plt.subplots()
    ppy.EphmatSpin.plot_phdisp(gaas_ephmat_spin, ax, show_qpoint_labels)

@pytest.mark.parametrize("kpoint_idx, show_qpoint_labels", [
                        (0, False),
                        (2, True)
])
def test_plot_defpot(gaas_ephmat_spin, plt, kpoint_idx, show_qpoint_labels, with_plt):
    """
    Method to test EphmatSpin.plot_defpot function
    
    Method to plot the deformation potential as a colormap overlaid on the phonon dispersion.

    kpoint_idx : int, optional
        Index of the k-point to plot the deformation potentials for. Deformation potentials will be plotted along q-points, at this k-point
        By default, it will be the first k-point.

    show_qpoint_labels : bool, optional
        If true, the q-point labels stored in the labels attribute will be shown on the plot. Default true.

    """
    
    if not with_plt:
        pytest.skip("Test requires pytest-plt")

    fig, ax = plt.subplots()
    ppy.EphmatSpin.plot_defpot(gaas_ephmat_spin, ax, kpoint_idx, show_qpoint_labels)

@pytest.mark.parametrize("kpoint_idx, show_qpoint_labels", [
                        (0, False),
                        (2, True)
])
def test_plot_ephmat(gaas_ephmat_spin, plt, kpoint_idx, show_qpoint_labels, with_plt):
    """
    Method to test EphmatSpin.plot_ephmat function
    
    Method to plot the e-ph spin flip matrix elements as a colormap overlaid on the phonon dispersion.

    kpoint_idx : int, optional
        Index of the k-point to plot the deformation potentials for. Deformation potentials will be plotted along q-points, at this k-point
        By default, it will be the first k-point.

    show_qpoint_labels : bool, optional
        If true, the q-point labels stored in the labels attribute will be shown on the plot. Default true.

    """
    
    if not with_plt:
        pytest.skip("Test requires pytest-plt")

    fig, ax = plt.subplots()
    ppy.EphmatSpin.plot_ephmat(gaas_ephmat_spin, ax, kpoint_idx, show_qpoint_labels)


def test_to_hdf5_mode_resolved(gaas_ephmat_spin, tmp_path):
    h5_path = tmp_path / "gaas_ephmat_spin_mode_resolved.h5"
    gaas_ephmat_spin.to_hdf5(h5_path)

    with h5py.File(h5_path, "r") as h5f:
        assert "phonon_mode" in h5f
        mode_keys = sorted(h5f["phonon_mode"].keys())
        assert len(mode_keys) == len(gaas_ephmat_spin.ephmat.keys())
        assert mode_keys[0] == "1"

        mode_1 = h5f["phonon_mode"]["1"]
        np.testing.assert_allclose(mode_1["ephmat"][()], gaas_ephmat_spin.ephmat[1])
        np.testing.assert_allclose(mode_1["defpot"][()], gaas_ephmat_spin.defpot[1])
        np.testing.assert_allclose(mode_1["phonon_energy"][()], gaas_ephmat_spin.phdisp[1])
