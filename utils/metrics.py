import numpy as np
import os
from utils.frequency import get_orig_frequencies
import bids
import mne
from tqdm import tqdm
import re

from crosspy.core._core import HAS_CUPY
from crosspy.preprocessing.signal import filter_data
from crosspy.core.synchrony import cplv

if HAS_CUPY:
    import cupy as cp

mne.set_log_level("ERROR")

def load_spiky_windows(sub: str, ses: str, task: str, run: str, bids_root: str) -> np.ndarray[bool]:
    """Load boolean mask for spiky windows in a time series.

    Args:
        sub (str): The subject for which to load information. BIDS format (e.g., "01").
        ses (str): The session for which to load information. BIDS format (e.g., "01").
        task (str): The task for which to load information. BIDS format (e.g., "ipd").
        run (str): The run for which to load information. BIDS format (e.g., "01").
        bids_root (str): The root path of the BIDS dataset.

    Returns:
        numpy.ndarray: Spiky windows mask. "0" if spiky, "1" otherwise.
    """
    mask_path = os.path.join(bids_root, "derivatives", "spiky_windows", f"sub-{sub}", f'sub-{sub}_ses-{ses}_task-{task}_run-{run}_spiky-windows.npy')
    mask = np.load(mask_path)

    return mask

def load_artefact_windows(sub: str, ses: str, task: str, run: str, bids_root: str) -> np.ndarray[bool]:
    """Load boolean mask for concatenation artefact windows in a time series.

    Args:
        sub (str): The subject for which to load information. BIDS format (e.g., "01").
        ses (str): The session for which to load information. BIDS format (e.g., "01").
        task (str): The task for which to load information. BIDS format (e.g., "ipd").
        run (str): The run for which to load information. BIDS format (e.g., "01").
        bids_root (str): The root path of the BIDS dataset.

    Returns:
        numpy.ndarray: Concatenation artefact windows mask. "0" if artefact, "1" otherwise.
    """
    mask_path = os.path.join(bids_root, "derivatives", "concatenationArtefactMask", f"sub-{sub}", f'sub-{sub}_ses-{ses}_task-{task}_run-{run}_concatenationArtefactMask.npy')
    mask = np.load(mask_path)

    return mask

def extract_wdw_related_name(event_path, wdw_length, ratio_wdw_overlap):

    folder_name = os.path.basename(os.path.normpath(event_path))
    match = re.search(r"b(\d+)a(\d+)", folder_name)
    if match:
        preEventTime = int(match.group(1))
        postEventTime = int(match.group(2))
    n_ep = ((preEventTime + postEventTime) - wdw_length * ratio_wdw_overlap) / (wdw_length * (1 - ratio_wdw_overlap))
    wdw_related_name = f'wdwed{wdw_length}sec{int(ratio_wdw_overlap*100)}over' if n_ep > 1 else 'nowdwed'

    return wdw_related_name

def compute_cplv(event_path: str, wdw_length: int, ratio_wdw_overlap: float, proc: str, suffix: str, ext: str):

    freqs = get_orig_frequencies()

    layout = bids.BIDSLayout(root=event_path, derivatives=True, validate=False)

    subjects = layout.get_subjects()
    for sub in tqdm(subjects, desc="Subjects", unit="sub", total=len(subjects), position=0):
        sessions = layout.get_sessions(subject=sub)
        for ses in sessions:
            tasks = layout.get_tasks(subject=sub, session=ses)
            for task in tasks:
                runs = layout.get_runs(subject = sub, session=ses, task = task)
                for run in runs:             
                
                    out_folder = os.path.join(event_path, r'derivatives', f"cPLV",f'sub-{sub}')                    
                    out_file = os.path.join(out_folder, f"sub-{sub}_ses-{ses}_task-{task}_run-{run}_cPLV.npy")
                    os.makedirs(out_folder, exist_ok=True)

                    if os.path.isfile(out_file):
                        print('The file already exists!')
                    else:
                        raw_path = layout.get(subject=sub, session=ses, task=task, run=run, proc=proc, suffix=suffix, extension=ext, return_type="filename")

                        raw_bip_ref = mne.io.read_raw_fif(raw_path[0], preload=False)

                        sfreq = raw_bip_ref.info['sfreq']
                        n_chs = len(raw_bip_ref.ch_names)
                        data = raw_bip_ref.get_data()[..., :-1]
                        
                        wdw_overlap = wdw_length * ratio_wdw_overlap
                        n_epochs = int(((data.shape[-1]/sfreq)-wdw_overlap)/(wdw_length-wdw_overlap))

                        data_epoch = np.zeros((n_epochs, n_chs, int(wdw_length*sfreq)))
                        for epoch_idx in range(n_epochs):
                            start_index = int(epoch_idx * (wdw_length - wdw_overlap)*sfreq)
                            end_index = int(start_index + wdw_length*sfreq)
                    
                            data_epoch[epoch_idx, ...] = data[..., start_index:end_index]
                
                        cplv_obs, cplv_sur = [cp.ndarray((n_epochs, n_chs, n_chs, len(freqs)), dtype=complex) for _ in range(2)]

                        for freq_idx, freq in enumerate(freqs):
                            for epoch_idx in range(n_epochs):
                                morlet = filter_data(x=data_epoch[epoch_idx, ...], sfreq=sfreq, frequency=freq, omega=7.5, n_jobs='cuda')
                        
                                cplv_obs[epoch_idx, :, :, freq_idx] = cplv(morlet)

                                cplv_sur[epoch_idx, :, :, freq_idx] = cplv(morlet, surr=True)
                        
                        np.save(out_file, [cplv_obs.get(), cplv_sur.get()])

    return