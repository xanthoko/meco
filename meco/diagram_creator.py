from typing import Optional
from plantuml import PlantUML


class PlantUMLClient:
    def __init__(self):
        url = 'http://www.plantuml.com/plantuml/img/'
        self.client = PlantUML(url)

    def make_diagram(self, txt_path: str, output_path: Optional[str] = None):
        self.client.processes_file(txt_path, outfile=output_path)
