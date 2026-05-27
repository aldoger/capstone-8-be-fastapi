import onnxruntime as ort
import numpy as np
import cv2
import supervision as sv

class ONNXRuntime:
    def __init__(self, model_path, inference_size, conf_threshold, target_class_ids):
        options = ort.SessionOptions()
        options.log_severity_level = 3 
        
        self.session = ort.InferenceSession(
            model_path, 
            sess_options=options,
            providers=['CUDAExecutionProvider', 'CPUExecutionProvider']
        )
        
        self.input_name = self.session.get_inputs()[0].name
        self.inference_size = inference_size
        self.conf_threshold = conf_threshold
        self.target_class_ids = target_class_ids
        
        print(f"[INFO] Active Provider: {self.session.get_providers()[0]}")

    def preprocess(self, frame_rgb):
        input_img = cv2.resize(frame_rgb, self.inference_size)
        input_tensor = input_img.astype(np.float32) / 255.0
        input_tensor = np.transpose(input_tensor, (2, 0, 1))
        input_tensor = np.expand_dims(input_tensor, axis=0)
        return input_tensor

    def postprocess(self, outputs, display_size):
        raw_boxes, raw_logits = outputs[0][0], outputs[1][0]

        # Sigmoid math
        probabilities = 1 / (1 + np.exp(-np.clip(raw_logits, -50, 50)))
        scores = np.max(probabilities, axis=1)
        class_ids = np.argmax(probabilities, axis=1)

        # Filtering
        mask = scores > self.conf_threshold
        filtered_boxes = raw_boxes[mask]
        
        if len(filtered_boxes) == 0:
            return sv.Detections.empty()

        # Box conversion
        cx, cy = filtered_boxes[:, 0], filtered_boxes[:, 1]
        w, h = filtered_boxes[:, 2], filtered_boxes[:, 3]

        x_min, y_min = cx - (w / 2), cy - (h / 2)
        x_max, y_max = cx + (w / 2), cy + (h / 2)

        # Scale to display
        disp_w, disp_h = display_size
        x_min *= disp_w
        x_max *= disp_w
        y_min *= disp_h
        y_max *= disp_h

        xyxy = np.stack([x_min, y_min, x_max, y_max], axis=1)

        detections = sv.Detections(
            xyxy=xyxy,
            confidence=scores[mask],
            class_id=class_ids[mask].astype(int)
        )

        filtered_class = np.isin(detections.class_id, self.target_class_ids)
        detections = detections[filtered_class]
        
        return detections

    def predict(self, frame_bgr, display_size):
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        input_tensor = self.preprocess(frame_rgb)
        outputs = self.session.run(None, {self.input_name: input_tensor})
        return self.postprocess(outputs, display_size)