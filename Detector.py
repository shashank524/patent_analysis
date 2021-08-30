# Detectron2 inference file

from detectron2.utils.logger import setup_logger
setup_logger()
from detectron2.config import get_cfg
from detectron2.engine import DefaultPredictor
from detectron2.data import MetadataCatalog
from detectron2.utils.visualizer import ColorMode, Visualizer
# from detectron2 import model_zoo

import cv2
import  numpy as np
import os


class Detector:
    def __init__(self):
        self.cfg = get_cfg()

        # Load config and model
        self.cfg.merge_from_file('./detectron2_data/config.yaml')
        # #self.cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url('COCO-Detection/faster_rcnn_R_101_FPN_3x.yaml')
        # self.cfg.MODEL.WEIGHTS = './model_final.pth'

        self.cfg.MODEL.WEIGHTS = './detectron2_data/model_final.pth'
        self.cfg.DATASETS.TEST = ("my_dataset_test", )
        self.cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.8   # set the testing threshold for this model

        self.cfg.MODEL.DEVICE = "cpu" # Change to cpu while deploying

        self.predictor = DefaultPredictor(self.cfg)
        MetadataCatalog.get(self.cfg.DATASETS.TRAIN[0]).thing_classes = ['cells', 'intermediates', 'markush-structures', 'reactions', 'relevant-structures', 'substitues']
        self.metadata = MetadataCatalog.get(self.cfg.DATASETS.TRAIN[0])

    def onImage(self, imagePath, saveDir, fileName, save_crop=False):
        image = cv2.imread(imagePath)
        predictions = self.predictor(image)

        viz = Visualizer(image[:,:,::-1], metadata = self.metadata, scale = 1)        
        output = viz.draw_instance_predictions(predictions["instances"].to("cpu"))
        save_path = saveDir + '/' + fileName
        cv2.imwrite(save_path, output.get_image()[:,:,::-1])
        
        if save_crop:
            image = image[:,:,::-1]
            # Getting Boxes
            boxes = predictions['instances'].pred_boxes
            # Getting Classes
            classes = predictions['instances'].pred_classes
            # print(classes)
            i=0
            for box in boxes:
                # Cropping the image
                x1, y1, x2, y2 = int(box[0]), int(box[1]), int(box[2]), int(box[3])
                cropped = image[y1:y2, x1:x2]
                # Getting the detected class
                detected_class_index = classes[i].item()
                detected_class = MetadataCatalog.get(self.cfg.DATASETS.TRAIN[0]).thing_classes[detected_class_index]
                # cv2_imshow(cropped)
                # print(detected_class)

                # Saving the cropped detections
                
                crop_save_dir = saveDir+'/'+detected_class
                
                if not os.path.exists(crop_save_dir):
                    os.mkdir(crop_save_dir)
                crop_path = crop_save_dir+'/'+fileName[:-4]+'_'+str(i)+'.jpg'

                cv2.imwrite(crop_path, cropped)

