import cv2 
import numpy as np
from .BboxUtils import measure_euclidean_distance, calculate_center_point


class Annotations(object):

    ''' Module to handle detection annotations and their styling attributes for easier visual digestion. '''

    def __init__(self):
        
        # Key value pairs for bounding box colours and their purpose.
        self.bbox_colours = {
            'standard' : (10, 255, 10),
            'offender' : (10, 10, 255),
            'trail' : (255, 10, 10)
        }

        # Endless styling attributes.
        self.min_corner_radius = 5
        self.max_corner_radius = 30
        self.border_radius = 6
        self.center_point_radius = 5

        self.min_thickness = 1
        self.max_thickness = 5

        self.font = cv2.FONT_HERSHEY_DUPLEX
        self.font_scale = 2
        self.font_colour = (255, 255, 255)
        self.font_thickness = 2

        self.bg_colour = (0,0,0)

        self.label_padding = 25
        self.padding = 64

        self.trail_thickness = 12
        self.end_point_thickness = 24
        self.size_factor = 0.5
        self.thickness_factor = 0.01
        self.thickness = 8


    def annotate_frame(self, frame : np.ndarray, detections : list[dict]) -> np.ndarray:

        ''' 
            Abstracted function to iterated over detections being ingested and apply annotation functions to render
                bbox corners and the labels pertaining to the paramaterised vision type selected by the user.

            * Paramaters:
                * frame : (np.ndarray) : Raw frame from the media being processed.
                * detections : (list[dict]) : Detection list enscapsulating dictionaries.
                * vision_type : (str) : Set vision_type from UI.
            * Returns:
                * annotated_frame : (np.ndarray) : Processed frame with bbox and labels rendered.
        '''
        
        for detection in detections:

            # Annotate vehicle corners.
            frame = self.annotate_bbox_corners(frame, detection)

            # Annotate metadata labels.
            frame = self.annotate_label(frame, detection, 'object_detection')

        # Return annotated frame. 
        return frame
    
            
    def annotate_bbox_corners(self, frame : np.ndarray, detection : dict) -> np.ndarray:

        '''
            Dynamically annotate a given detection adjusting the size and border radius of the annotated bounding box in relativity to 
                the detections size. 

            Parameters: 
                * frame : (np.ndarray) : frame to be drawn upon.
                * detection : (dict) : detection dictionary containing desired values to plot data points.
            
            Returns:
                * annotated_frame : (np.ndarray) : Annotated frame with a detections given bounding box. 
        '''

        latest_bbox = detection['bboxes']
        # Fetch detection bounding box values, typecast to full integer values. 
        x1, y1, x2, y2 = (
            int(latest_bbox['x1']),
            int(latest_bbox['y1']),
            int(latest_bbox['x2']),
            int(latest_bbox['y2']),
        )

        # Calculate detection dimensions.
        detection_size = min(x2 - x1, y2 - y1)

        # Dynamically calculate a detections line thickness and corner radius for annotation.
        corner_radius = max(min(int(detection_size * self.size_factor), self.max_corner_radius), self.min_corner_radius)
        thickness = max(min(int(detection_size * self.thickness_factor) * 2, self.max_thickness), self.min_thickness)

        # Fetch appropriate colour for detection.
        colour = self.bbox_colours['standard']     

        # Store corner values within a list.
        bbox_corners = [
            ((x1 + corner_radius, y1 + corner_radius), 180, 270),

            ((x1 + corner_radius, y2 - corner_radius), 90, 180),
            ((x2 - corner_radius, y1 + corner_radius), 270, 360),
            ((x2 - corner_radius, y2 - corner_radius), 0, 90)
        ]
        
        # Iterate over bbox corner values, annotate with ellipses.
        for (center_x, center_y), start_angle, end_angle in bbox_corners:

            cv2.ellipse(
                frame, 
                (int(center_x), int(center_y)),
                (corner_radius, corner_radius),
                0, start_angle, end_angle,
                colour, 
                thickness
            )

        # Return modified frame with bbox corners. 
        return frame
    

    def fetch_text_properties(self, label : str, frame : np.ndarray) -> tuple[tuple[int, int], float]:
        
        '''
            Function to ingest label text, the current frame being processed and infer the appropriate 
            properties for the text properties so they can be scaled accordingly.

            Paramaters:
                * label : (str) : The concerned label to be rendered and the text it is comprised of.
                * frame : (np.ndarray) : The current frame being processed.
            Returns:
                * (text_width, text_height), current_font_scale : (tuple[tuple[int, int], float]) : Returns the 
                    height and width of the text. Alongside, the current, appropriate font scale.
        '''

        # Set current font scale to the base value.
        current_font_scale = self.font_scale
        # Minumum threshold.
        min_font_scale = 0.8
        # Max width threshoold based of padding and frame width values.
        max_text_width = frame.shape[1] - self.label_padding * 2

        # Fetch text dimensions from cv2 BIF.
        text_width, text_height = cv2.getTextSize(label, self.font, current_font_scale, self.font_thickness)[0]

        # While the current properties exceed their thresholds. Update them accordingly.
        while text_width > max_text_width and current_font_scale > min_font_scale:
            
            # Gradually decrement font scale.
            current_font_scale -= 0.1
            # Assign updated text dimension properties.
            text_width, text_height = cv2.getTextSize(label, self.font, current_font_scale, self.font_thickness)[0]

        # Return values for users access. 
        return (text_width, text_height), current_font_scale
    

    def calculate_label_position(self, bbox_bottom : int, center_point : tuple[float, float], text_size : tuple[float, float]) -> dict[str, int]:

        '''
            Calculate current label position for a given detection bbox value.

            Paramaters:
                * bbox_bottom : (int) : Specific, single, coordinate representing bottom of the detection bounding box.
                * center_point : (tuple[float, float]) : Detections current center point value.
                * text_size : (tuple[float, float]) : Dimensions of the text being processed to pad out the label distance appropriately.
            Returns:
                * label_position : (dict[int) : Returns dictionary containing updated label x1, y1, w, h values to 
                    align it with a detection accordingly.
        '''

        # Unpack text size values.
        text_width, text_height = text_size

        # Update label position dictionary based off current center point and text size values.
        return {
            'x' : int(center_point[0] - text_width // 2), 'y' : int(bbox_bottom + text_height + self.label_padding),
            'width' : text_width + 2 * self.label_padding, 'height' : text_height + 2 * self.label_padding
        }
    

    def get_label_dimensions(self, label : str, frame : np.ndarray) -> tuple[float, float]:

        '''
            Fetch label dimensions from the text properties paramaterised.

            Paramaters:
                * label : (str) : The text to be given to the label.
                * frame : (np.ndarray) : Current frame being processed.
            Returns:
                * box_width, box_height : (tuple[float, float]) : Dimensions for the label calculated from text properties.
        '''
        
        # Fetch text width and height properties.
        text_width, text_height = self.fetch_text_properties(label, frame)[0]

        # Apply label padding attributes to calculated values.
        box_width = text_width + 2 * self.label_padding
        box_height = text_height + 2 * self.label_padding

        # Return final label dimension values. 
        return box_width, box_height


    def draw_label_background(self, frame : np.ndarray, position : dict[float]) -> np.ndarray:

        ''' 
            Draw background for label leveraging cv2 BIFs to apply border radius styling to make things
                look fancier. 

            Paramaters:
                * frame : (np.ndarray) : Current frame being processed.
                * position : (dict[float]) : Label position dictionary data enscapsulating x1, y1, w, h
            Returns:
                * annotated_frame : (np.ndarray) : Processed frame where label backgrounds have been rendered.
        '''

        # Unpack label dimension and cooordinate values.
        x, y, w, h = (position['x'], position['y'], position['width'], position['height'])

        cv2.rectangle(frame, (x + self.border_radius, y), ( x + w - self.border_radius, y + h), self.bg_colour, -1)
        cv2.rectangle(frame, (x, y + self.border_radius), (x + w, y + h - self.border_radius), self.bg_colour, -1)

        # Store label corner data in a list to iterate upon.
        label_corners = [
            # top left.
            (x + self.border_radius, y + self.border_radius, 180, 270),
            # top right.
            (x + w - self.border_radius, y + self.border_radius, 270, 360),
            # bottom left.
            (x + self.border_radius, y + h - self.border_radius, 90, 180),
            # bottom right.
            (x + w - self.border_radius, y + h - self.border_radius, 0, 90)
        ]

        # Iterate over data points within the label_corners list.
        for center_x, center_y, start_angle, end_angle in label_corners:
            
            # Render each corner as an ellipses.
            cv2.ellipse(
                frame, 
                (center_x, center_y),
                (self.border_radius, self.border_radius),
                0, start_angle, end_angle,
                self.bg_colour,
                -1
            )

        # Return modified frame with label renderings. 
        return frame


    def draw_label_text(self, frame : np.ndarray, label : str, position : tuple[float], text_size : tuple[float, float], font_scale : float) -> np.ndarray:

        '''
            Append label text onto label background leveraging cv2 BIF.

            Paramaters:
                * frame : (np.ndarray) : Frame to have text drawn upon.
                * label : (str) : Label text to be rendered upon frame.
                * position : (tuple[float]) Label coordinates x1, y1, w, h
                * text_size : (tuple[float, float]) : text dimensions width and height.
                * font_scale : (float) : Current, updated font scale to modify text size.
            Returns:
                * annotated_frame : (np.ndarray) : Frame with text rendered.
        '''

        # Unpack text x1 and y1 values to place text.
        text_x = position['x'] + self.label_padding
        text_y = position['y'] + text_size[1] + self.label_padding

        # Utilise cv2 to draw text upon label.
        cv2.putText(
            frame,
            label,
            (text_x, text_y),
            self.font,
            font_scale,
            self.font_colour,
            self.font_thickness,
            lineType=cv2.LINE_AA
        )

        # Return annotated frame.
        return frame

    
    def annotate_label(self, frame : np.ndarray, detection : dict, vision_type : str) -> np.ndarray:

        '''
            Leverage both helper functions, combining them together to render label background 
                and the concerned label. Ensuring the position, dimensions are always up to scale
                with detections.

            Paramaters:
                * frame : (np.ndarray) : Frame to have labels rendered.
                * detection : (dict) : Detection to be annotated.
                * vision_type : (str) : Label type required.
            Returns:
                * annotated_frame : (np.ndarray) : Updated frame with label annotated.
        '''

        # Fetch appropriate detection label dependant on vision_type.
        detection_label = self.create_label(detection=detection, vision_type=vision_type)

        latest_bbox = detection['bboxes']

        # Fetch detection bounding box values, typecast to full integer values. 
        x1, y1, x2, y2 = (
            int(latest_bbox['x1']),
            int(latest_bbox['y1']),
            int(latest_bbox['x2']),
            int(latest_bbox['y2']),
        )

        # Fetch detection center point values.
        center_x, center_y = calculate_center_point(detection)

        # Fetch text dimensions and scale.
        text_size, font_scale = self.fetch_text_properties(detection_label, frame)
        # Calculate appropriate label position.
        label_position = self.calculate_label_position(y2, (center_x, center_y), text_size)

        # Draw label background and text.
        frame = self.draw_label_background(frame, label_position)
        frame = self.draw_label_text(frame, detection_label, label_position, text_size, font_scale)

        # Return frame where renderings have been made.
        return frame
    

    def create_label(self, detection : dict, vision_type : str) -> str:

        '''
            Generate appropriate label to support required vision type.

            Paramaters:
                * detection : (dict) : Concerned detection to access its metadata.
                * vision_type : (str) : String key value to access required label.
            Returns:
                * label : (str) : String of required data values for annotation.
        '''
        # Dictionary containing key pair values of vision_types and their concerned labels.
        detection_labels = {
            'object_detection': f"ID : {detection.get('ID', 0)}, Threat Level: {detection.get('threat_level', 0)}",
        }

        # Return label from given vision type.
        return detection_labels.get(vision_type, 'object_detection')
