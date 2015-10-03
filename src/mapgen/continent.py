from node import Node
import random
import game_constants


class Continent():

    # Generates a continent
    # ARGS - Graph Object, Number of ISPs per continent, Number of cities per ISP

    def __init__(self, graph, num_ISPs, max_cities_per_ISP, total_power_per_ISP):
        # Init object lists
        self.isp_list = []  # Contains ISP objects
        self.datacenter_list = []  # Contains DC objects
        self.isps_city_list = []  # Contains list of cities objects, the index of ISP is the index of its city list

        # Generates num_ISPs ISPs and DCs
        # It maintains a circular connection, (For easy of visualization)
        # For example, ISP 1 connects to ISP 2 and DC 1, so on and so on
        for _ in range(num_ISPs):
            isp = self.generate_ISP(graph, max_cities_per_ISP, total_power_per_ISP)  # Generate ISP
            datacenter = self.generate_datacenter(graph)  # Generate DC

            self.isp_list.append(isp)  # Add ISP to list
            self.datacenter_list.append(datacenter)  # Add DC to list

            graph.add_edge(isp, datacenter)  # Connect the ISP and DC
            if len(self.isp_list) != 1:
                graph.add_edge(isp, self.isp_list[-2])  # Connect ISP with previous ISP
                graph.add_edge(datacenter, self.datacenter_list[-2])  # Connect DC with previous DC
        if len(self.isp_list) > 1:  # connect ends of list to make circular
            graph.add_edge(self.isp_list[0], self.isp_list[-1])
            graph.add_edge(self.datacenter_list[0], self.datacenter_list[-1])

    # Generates a ISP and its cities
    # ARGS - Graph Object, Number of cities per ISP
    def generate_ISP(self, graph, max_cities_per_ISP, total_power_per_ISP):
        isp = Node.get_ISP_node(graph)  # Create a ISP
        isp_city_list = []  # Init city list for ISPs
        temp_city_list = []
        aprox_total_power_per_ISP = total_power_per_ISP - total_power_per_ISP % 100
        current_power = 0
        while(aprox_total_power_per_ISP != current_power):
            rand = random.randrange(0, 3)
            node_type = ""
            if (rand == 0):
                node_type = "Large City"
            elif (rand == 1):
                node_type = "Medium City"
            else:
                node_type = "Small City"

            temp_city_list.append(node_type)
            current_power += game_constants.NodeType.processing[node_type]

            if aprox_total_power_per_ISP < current_power:
                removed_node = temp_city_list.pop(len(isp_city_list) - 1)
                current_power -= game_constants.NodeType.processing[removed_node]

            if len(temp_city_list) > max_cities_per_ISP:
                temp_city_list = []
                current_power = 0

        for node_type in temp_city_list:
            if node_type == "Large City": 
                isp_city_list.append(Node.get_large_city_node(graph))  # Generate city for the ISP
            elif node_type == "Medium City":
                isp_city_list.append(Node.get_medium_city_node(graph))  # Generate city for the ISP
            elif node_type == "Small City":
                isp_city_list.append(Node.get_small_city_node(graph))  # Generate city for the ISP

        # Make the ISPs and cities of the ISP a fully connected graph
        for city1 in isp_city_list:
            graph.add_edge(isp, city1)
            for city2 in isp_city_list:
                if city1.uid is not city2.uid:
                    graph.add_edge(city1, city2)
        self.isps_city_list.append(isp_city_list)

        return isp

    def generate_datacenter(self, graph):
        return Node.get_DC_node(graph)

    # Connect two continents given unique isps per continent
    def connect_continent(self, graph, continent, r_isp, s_isp, r_per_isp, s_per_isp):
        # Check if there is enough isps to connect each other
        if s_isp > len(self.isp_list):
            raise Exception('Invalid number of edges for isp1')
        if r_isp > len(continent.isp_list):
            raise Exception('Invalid number of edges for isp2')

        used_isp_list_send = []  # Init list of used ISPs for sending
        used_isp_list_recv = []  # Init list of used ISPs for recving
        if r_isp > s_isp:
            # Connect ISPs until we have the needed amount
            while len(used_isp_list_send) != s_isp:

                isp1 = self.get_random_isp()
                while isp1.uid in used_isp_list_send:
                    isp1 = self.get_random_isp()  # Get ISPs until we find one that we are not using

                isp2 = continent.get_random_isp()
                while isp2.uid in used_isp_list_recv:
                    isp2 = continent.get_random_isp()  # Same as before

                used_isp_list_send.append(isp1.uid)
                used_isp_list_recv.append(isp2.uid)

                self.connent_continent_isp(graph, continent, isp1, isp2, s_per_isp, r_per_isp)
            # For the rest of the ISPs connect the rest of the ISPs with already used ISpS
            for _ in range(r_isp - s_isp):
                used_isp_list_send = random.shuffle(used_isp_list_send)
                isp1 = used_isp_list_send[0]

                isp2 = continent.get_random_isp()
                while isp2.uid not in used_isp_list_recv:
                    isp2 = continent.get_random_isp()

                used_isp_list_recv.append(isp2.uid)

                self.connent_continent_isp(graph, continent, isp1, isp2, s_per_isp, r_per_isp)
        else:  # Same as above just other way around
            while len(used_isp_list_recv) != r_isp:
                isp1 = self.get_random_isp()
                while isp1.uid in used_isp_list_send:
                    isp1 = self.get_random_isp()

                isp2 = continent.get_random_isp()
                while isp2.uid in used_isp_list_recv:
                    isp2 = continent.get_random_isp()

                used_isp_list_send.append(isp1.uid)
                used_isp_list_recv.append(isp2.uid)

                self.connent_continent_isp(graph, continent, isp1, isp2, s_per_isp, r_per_isp)
            for _ in range(s_isp - r_isp):
                used_isp_list_recv = random.shuffle(used_isp_list_recv)

                isp1 = used_isp_list_recv[0]
                isp2 = self.get_random_isp()

                while isp2.uid not in used_isp_list_send:
                    isp2 = self.get_random_isp()

                used_isp_list_send.append(isp2.uid)

                self.connent_continent_isp(graph, continent, isp2, isp1, s_per_isp, r_per_isp)

    # Connects two isps given a number of cities to connect for each isp
    def connent_continent_isp(self, graph, continent, isp1, isp2, unique_cities_isp1, unique_cities_isp2):
        # Check if there is enough cities per ISP to connect
        if unique_cities_isp1 > len(self.isps_city_list[self.isp_list.index(isp1)]):
            raise Exception('Invalid number of edges for isp1')
        if unique_cities_isp2 > len(continent.isps_city_list[continent.isp_list.index(isp2)]):
            raise Exception('Invalid number of edges for isp2')

        used_city_list_isp1 = []  # Init list of used cities for isp1
        used_city_list_isp2 = []  # Init list of used cities for isp2
        if unique_cities_isp2 > unique_cities_isp1:
            # Connect cities until the min value is reached
            while len(used_city_list_isp1) != unique_cities_isp1:
                city1 = self.get_random_city(isp1)
                while city1.uid in used_city_list_isp1:
                    city1 = self.get_random_city(isp1)

                city2 = continent.get_random_city(isp2)
                while city2.uid in used_city_list_isp2:
                    city2 = continent.get_random_city(isp2)

                used_city_list_isp1.append(city1.uid)
                used_city_list_isp2.append(city2.uid)

                graph.add_edge(city1, city2)

            # Connect rest of cities with already used cities for isp1
            for _ in range(unique_cities_isp2 - unique_cities_isp1):
                used_city_list_isp1 = random.shuffle(used_city_list_isp1)
                city1 = used_city_list_isp1[0]

                city2 = continent.get_random_city(isp2)
                while city2.uid in used_city_list_isp2:
                    city2 = continent.get_random_city(isp2)

                used_city_list_isp2.append(city2.uid)

                graph.add_edge(city1, city2)
        else:  # Same as above except other way around
            while len(used_city_list_isp2) != unique_cities_isp2:
                city2 = continent.get_random_city(isp2)
                while city2.uid in used_city_list_isp2:
                    city2 = continent.get_random_city(isp2)

                city1 = self.get_random_city(isp1)
                while city1.uid in used_city_list_isp1:
                    city1 = self.get_random_city(isp1)

                used_city_list_isp2.append(city2.uid)
                used_city_list_isp1.append(city1.uid)

                graph.add_edge(city2, city1)
            for _ in range(unique_cities_isp1 - unique_cities_isp2):
                used_city_list_isp2 = random.shuffle(used_city_list_isp2)
                city2 = used_city_list_isp2[0]

                city1 = self.get_random_city(isp1)
                while city1.uid in used_city_list_isp1:
                    city1 = self.get_random_city(isp1)

                used_city_list_isp1.append(city1.uid)

                graph.add_edge(city2, city1)

    # Return random isp
    def get_random_isp(self):
        return self.isp_list[random.randint(0, len(self.isp_list) - 1)]

    # Return random city
    # ARGS - Isp Object
    def get_random_city(self, isp=None):
        if isp is None:
            isp = self.get_random_isp()
        isp_index = self.isp_list.index(isp)
        return self.isps_city_list[isp_index][random.randint(0, len(self.isps_city_list[isp_index]) - 1)]

    # Return string rep of the continent
    # Not really used
    def __str__(self):
        s = ""
        for i in range(len(self.isp_list)):
            s += repr(self.isp_list[i])
            s += repr(self.isps_city_list[i]) + "\n"
        for i in range(len(self.datacenter_list)):
            s += repr(self.datacenter_list[i]) + "\n"
        return s

    # TODO Fix __repr__ and __str__
