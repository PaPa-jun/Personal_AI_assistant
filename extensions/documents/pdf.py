from ultralytics import YOLO
from .tree import Tree, Node
import os, fitz, tempfile, cv2, numpy as np

class PDFParser:
    """
        # Document structure analyzer.

        :param model_dir: Directory of the YOLO model.
        :param device: Device to run the model on (e.g., 'cuda' or 'cpu').
    """
    def __init__(self, model_dir, device) -> None:
        self.model = YOLO(model_dir)
        self.device = device
        self.temp_files: list  # List to store paths to temporary image files.

    def create_temp_images(self, source_dir, scale) -> None:
        """
        ## Generate temporary images from a PDF document.

        :param source_dir: Path to the source PDF document.
        :param scale: Scaling factor for the image generation.
        """
        doc = fitz.open(source_dir)
        self.temp_files = []

        for index, page in enumerate(doc):
            zoom_x = scale
            zoom_y = scale
            mat = fitz.Matrix(zoom_x, zoom_y).prerotate(int(0))  # Apply scaling and no rotation.
            pix = page.get_pixmap(matrix=mat, alpha=False)

            temp_filename = f"page-{index}.png"  # Create a filename for the temporary image.
            temp_file = os.path.join(tempfile.gettempdir(), temp_filename)
            self.temp_files.append(temp_file)  # Store the path of the temporary image.
            pix.save(temp_file)  # Save the image as a PNG file.

        doc.close()  # Close the PDF document.

    def save_predicted_images(self, source, index, save_dir) -> None:
        """
        ## Save the predicted bounding boxes and labels on the image.

        :param source: YOLO prediction result containing bounding boxes.
        :param index: Index of the image to save.
        :param save_dir: Directory to save the annotated image.
        """
        image = cv2.imread(self.temp_files[index])  # Read the temporary image.

        for box in source.boxes:
            xmin, ymin, xmax, ymax = box.xyxy.cpu().numpy().tolist()[0]  # Get bounding box coordinates.
            label = source.names[box.cls.cpu().numpy().tolist()[0]]  # Get the label for the class.
            conf = box.conf.cpu().numpy().tolist()[0]  # Get the confidence score.

            # Convert confidence to a hue value for coloring the box.
            hue = int(120 * (1 - conf))
            color = (hue, 255, 255)
            hsv_color = np.uint8([[color]])
            bgr_color = cv2.cvtColor(hsv_color, cv2.COLOR_HSV2BGR)[0][0]  # Convert HSV color to BGR.

            # Draw the bounding box and label on the image.
            cv2.rectangle(image, (int(xmin), int(ymin)), (int(xmax), int(ymax)), bgr_color.tolist(), 2)
            cv2.putText(image, f'{label} : {round(conf, 2)}', (int(xmin), int(ymin) - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, bgr_color.tolist(), 2)

        os.makedirs(save_dir, exist_ok=True)  # Ensure the save directory exists.
        cv2.imwrite(os.path.join(save_dir, f'page-{index}.jpg'), image)  # Save the annotated image.

    def analyze_document(self, source_dir, save_dir, scale) -> list:
        """
        ## Analyze a PDF document by predicting bounding boxes and extracting content.

        :param source_dir: Path to the source PDF document.
        :param save_dir: Directory to save the annotated images.
        :param scale: Scaling factor for image generation.
        :return: List of Tree structures representing the document layout.
        """
        self.create_temp_images(source_dir, scale)  # Generate temporary images.
        results = self.model.predict(source=self.temp_files, device=self.device, iou=0.3)  # Run YOLO model predictions.

        document = fitz.open(source_dir)
        trees = []

        for page, result in enumerate(results):
            self.save_predicted_images(result, page, save_dir)  # Save predicted bounding boxes on images.
            tree = Tree()  # Create a new Tree structure for the page.
            for box in result.boxes:
                # Create a Node for each detected bounding box.
                node = Node(
                    box=box.xyxy.cpu().numpy().tolist()[0], 
                    label=result.names[box.cls.cpu().numpy().tolist()[0]],
                    conf=box.conf.cpu().numpy().tolist()[0], 
                    cls=int(box.cls.cpu().numpy().tolist()[0])
                )
                # Define the region of the text within the bounding box.
                clip = fitz.Rect(node.box[0] / scale, node.box[1] / scale, node.box[2] / scale, node.box[3] / scale)
                content = document[page].get_textbox(clip)  # Extract text from the defined region.
                node.units.append(content)  # Append the extracted content to the node.
                tree.nodes.append(node)  # Append the node to the tree.

            tree.nodes.sort(key=lambda s: (s.box[1], s.box[0]))  # Sort nodes by vertical and horizontal position.
            trees.append(tree)  # Append the tree to the list of trees.

        for file in self.temp_files: 
            os.remove(file)  # Remove temporary image files.
        return trees  # Return the list of Tree structures.