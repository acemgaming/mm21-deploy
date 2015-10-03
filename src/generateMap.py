from mapgen.map import Map
import argparse
import load_json

parser = argparse.ArgumentParser(
    description="Launches the visualizer")
parser.add_argument(
    "-c", "--num_continents",
    help="Number of continents to use",
    default="12")
parser.add_argument(
    "-i", "--isp_per_continents",
    help="Number of isps per continents",
    default="3")
parser.add_argument(
    "-m", "--max_cities_per_isp",
    help="Number of cities per isp",
    default="6")
parser.add_argument(
    "-t", "--total_power_per_isp",
    help="Number power of cities per isp",
    default="1000")
args = parser.parse_args()  # parse args

if __name__ == "__main__":
    # Generate Map
    m = Map(int(args.num_continents), int(args.isp_per_continents), int(args.max_cities_per_isp), int(args.total_power_per_isp))

    # Convert to JSON
    load_json.save_map_to_file("gamerunner/map.json", m.convert_to_json())
