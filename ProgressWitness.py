#!/usr/bin/env python

"""
ProgressWitness - Make image snapshots of your image editing progress.
2022(c) by https://peakd.com/@quantumq
Compatibility: GIMP 2.10.x
"""

import glob, os, re
from gimpfu import *


def _progress_witness_set_progress(progressMessage, isEnd = False):
   """
   Updates the progress and sends a message about the step.

   :param progressMessage: The message text of the progress.
   :param isEnd: If "True" the progress will be completed after the message was sent.
   """

   pdb.gimp_progress_pulse()
   pdb.gimp_progress_set_text(progressMessage)
   if isEnd:
      pdb.gimp_progress_end()

def _progress_witness_make_incremental_filename(lookupPath, filenameTemplate):
   """
   Creates a file name with an incremental numeric suffix appended to it.
   The file number is determined by looking it up in a specific directory.

   :param lookupPath: The path of the directory to look into.
   :param filenameTemplate: The format template string for a filename. 
   :return str: The generated filename.
   """
   
   snapshotFilenames = glob.glob(os.path.join(lookupPath, "*.jpg"))
   suffixes = [0]
   for snapshotFilename in snapshotFilenames:
      i = os.path.splitext(snapshotFilename)[0]
      try:
         number = re.findall('[0-9]+$', i)[0]
         suffixes.append(int(number))
      except IndexError:
         pass
   suffixes = sorted(suffixes)
   newNum = suffixes[-1]+1

   return filenameTemplate.format(number=newNum)
   

def progress_witness(snapshotSizeInPercent):
   """
   The main function of the plugin.

   :param snapshotSizeInPercent: The scale factor of the snapshot in percent.
   """

   gimp.progress_init("Witnessing progress!")

   image = gimp.image_list()[0] 
   filename = pdb.gimp_image_get_filename(image)
   if filename is None:
      gimp.message('Please save the image project to a folder first.')
      _progress_witness_set_progress('Error: Please save the image project to a folder first.', True)
      return

   snapshotPath = os.path.join(os.path.dirname(os.path.abspath(filename)), 'snapshots')

   _progress_witness_set_progress('Making snapshot...')
   imageCopy = pdb.gimp_image_duplicate(image)
   allLayers = pdb.gimp_image_merge_visible_layers(imageCopy, 1)

   _progress_witness_set_progress('Resizing snapshot...')

   pdb.gimp_context_set_interpolation(0)
   pdb.gimp_image_scale(
      imageCopy, 
      int((float(pdb.gimp_image_width(imageCopy)) / 100.0) * snapshotSizeInPercent),
      int((float(pdb.gimp_image_height(imageCopy)) / 100.0) * snapshotSizeInPercent),
   )

   if not os.path.isdir(snapshotPath):
      os.mkdir(snapshotPath)

   _progress_witness_set_progress('Saving snapshot...')
   pdb.gimp_file_save(
      imageCopy, 
      allLayers, 
      os.path.join(snapshotPath, _progress_witness_make_incremental_filename(snapshotPath, 'snapshot{number}.jpg')), 
      '?'
   )

   _progress_witness_set_progress('Cleaning up...')
   pdb.gimp_image_delete(imageCopy)

   _progress_witness_set_progress('Finished!', True)


register(
    "progress_witness",
    "ProgressWitness",
    "Create an image snapshot of your image editing progress into a subfolder of the folder where your project is located.",
    "QuantumG",
    "QuantumG",
    "2022",
    "Witness progress",
    "RGB*",
    [
            (PF_SLIDER, "snapshotSizeInPercent", "Snapshot size in percent", 50, (5, 100, 1))
    ],
    [],
    progress_witness, menu="<Image>/Tools")

main()

