import cv2
import supervision as sv
from trackers import ByteTrackTracker, SORTTracker, OCSORTTracker

class Tracker:
    def __init__(self, activate, tracker):
        self.activate = activate
        if tracker == "ByteTrack":
            self.tracker = ByteTrackTracker(
                lost_track_buffer = 30,
                frame_rate = 30.0,
                track_activation_threshold = 0.7,
                minimum_consecutive_frames = 2,
                minimum_iou_threshold = 0.5,
                high_conf_det_threshold = 0.4,                
            )
        elif tracker == "SORT":
            self.tracker = SORTTracker(
                lost_track_buffer = 30,
                frame_rate = 30.0,
                track_activation_threshold = 0.7,
                minimum_consecutive_frames = 2,
                minimum_iou_threshold = 0.5,
            )
        elif tracker == "OC-SORT":
            self.tracker = OCSORTTracker(
                lost_track_buffer = 60,
                frame_rate = 30.0,
                minimum_consecutive_frames = 2,
                minimum_iou_threshold = 0.3,
                direction_consistency_weight = 0.2,
                high_conf_det_threshold = 0.3,
                delta_t = 3,                
            )

        self.box_annotator = sv.BoxAnnotator(
            thickness=1
        )
        self.label_annotator = sv.LabelAnnotator(
            text_thickness=1,
            text_scale=0.4,
            text_padding=1
        )

    def track_and_draw(self, frame, detections):
        if self.activate:
            # Update tracker
            detections = self.tracker.update(detections=detections)
            
            labels = [
                f"#{tracker_id} {conf:.2f}" 
                for tracker_id, conf in zip(detections.tracker_id, detections.confidence) 
            ]
        else:
            labels = [
                f"{conf:.2f}" 
                for conf in detections.confidence 
            ]        

        annotated = self.box_annotator.annotate(scene=frame.copy(), detections=detections)
        annotated = self.label_annotator.annotate(scene=annotated, detections=detections, labels=labels)

        # Draw Counter
        text = f"Total People: {len(detections)}"
        cv2.putText(
            img=annotated, text=text, org=(20, 50),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1.0,
            color=(0, 0, 0), thickness=2, lineType=cv2.LINE_AA
        )
        
        return annotated