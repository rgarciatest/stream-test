# /home/ax/SemanticGraphs/vis_graph/utils.py
# utility and helper functions for use in pyvis


# /home/ax/SemanticGraphs/vis_graph/network.py
import json
import os
import shutil
import tempfile
import webbrowser
from collections import defaultdict
import jsonpickle
import networkx as nx
from IPython.display import IFrame
from jinja2 import Environment, FileSystemLoader

def check_html(name):
    assert len(name.split(".")) >= 2, "invalid file type for %s" % name
    assert name.split(".")[-1] == "html", "%s is not a valid html file" % name

# /home/ax/SemanticGraphs/vis_graph/edge.py
class Edge(object):
    def __init__(self, source, dest, directed=False, edge_width = 1, **options):
        self.options = options
        self.options['from'] = source
        self.options['to'] = dest
        if directed:
            if 'arrows' not in self.options:
                self.options["arrows"] = "to"

        self.options['width'] = edge_width

# /home/ax/SemanticGraphs/vis_graph/node.py
class Node(object):
    def __init__(self, n_id, shape, label, node_size=40, font_color=False, font_size=35, **opts):
        self.options = opts
        self.options["id"] = n_id
        self.options["label"] = label
        self.options["shape"] = shape
        self.options["size"] = node_size
        self.options["font"] = dict(color=font_color, size=font_size)

# /home/ax/SemanticGraphs/vis_graph/physics.py
import json

class Physics(object):
    engine_chosen = False
    def __getitem__(self, item):
        return self.__dict__[item]
    
    def __repr__(self):
        return str(self.__dict__)

    class barnesHut(object):
        """BarnesHut is a quadtree based gravity model"""
        def __init__(self, params):
            self.gravitationalConstant = params["gravity"]
            self.centralGravity = params["central_gravity"]
            self.springLength = params["spring_length"]
            self.springConstant = params["spring_strength"]
            self.damping = params["damping"]
            self.avoidOverlap = params["overlap"]

    class Stabilization(object):
        def __getitem__(self, item):
            return self.__dict__[item]
        def __init__(self):
            self.enabled = True
            self.iterations = 1000
            self.updateInterval = 50
            self.onlyDynamicEdges = False
            self.fit = True

        def toggle_stabilization(self, status):
            self.enabled = status

    def __init__(self):
        self.enabled = True
        self.stabilization = self.Stabilization()

    def use_barnes_hut(self, params):
        self.barnesHut = self.barnesHut(params)

    def toggle_stabilization(self, status):
        self.stabilization.toggle_stabilization(status)

    def to_json(self):
        return json.dumps(
            self, default=lambda o: o.__dict__,
            sort_keys=True, indent=4)



# /home/ax/SemanticGraphs/vis_graph/options.py

class EdgeOptions(object):
    def __init__(self):
        self.smooth = self.Smooth()
        self.color = "#000000"

    def inherit_colors(self, status):
        self.color.inherit = status

    def set_edge_colors(self, color):
        self.color = color

    def toggle_smoothness(self, smooth_type):
        self.smooth.type = smooth_type

    def __repr__(self):
        return str(self.__dict__)

    class Smooth(object):
        def __repr__(self):
            return str(self.__dict__)

        def __init__(self):
            self.enabled = True
            self.type = "dynamic"

    class Color(object):
        def __repr__(self):
            return str(self.__dict__)

        def __init__(self):
            self.inherit = True

class Interaction(object):
    def __repr__(self):
        return str(self.__dict__)

    def __init__(self):
        self.hideEdgesOnDrag = False
        self.hideNodesOnDrag = False
        self.dragNodes = True

    def __getitem__(self, item):
        return self.__dict__[item]

class Configure(object):
    def __repr__(self):
        return str(self.__dict__)

    def __init__(self, enabled=False, filter_=None):
        self.enabled = enabled
        if filter_:
            self.filter = filter_ 

    def __getitem__(self, item):
        return self.__dict__[item]

class Layout(object):
    def __repr__(self):
        return str(self.__dict__)

    def __init__(self, randomSeed=None, improvedLayout=True):
        if not randomSeed: self.randomSeed = 0
        else: self.randomSeed = randomSeed
        self.improvedLayout = improvedLayout
        self.hierarchical = self.Hierarchical(enabled=True)
    
    def set_separation(self, distance):
        self.hierarchical.levelSeparation = distance
    
    def set_tree_spacing(self, distance):
        self.hierarchical.treeSpacing = distance

    def set_edge_minimization(self, status):
        self.hierarchical.edgeMinimization = status

    class Hierarchical(object):
        def __getitem__(self, item):
            return self.__dict__[item]

        def __init__(self,
                    enabled=False,
                    levelSeparation=150,
                    treeSpacing=200,
                    blockShifting=True,
                    edgeMinimization=True,
                    parentCentralization=True,
                    sortMethod='hubsize'):

            self.enabled = enabled
            self.levelSeparation = levelSeparation
            self.treeSpacing = treeSpacing
            self.blockShifting = blockShifting
            self.edgeMinimization = edgeMinimization
            self.parentCentralization = parentCentralization
            self.sortMethod = sortMethod

class Options(object):
    def __repr__(self):
        return str(self.__dict__)

    def __getitem__(self, item):
        return self.__dict__[item]

    def __init__(self, layout=None):
        if layout: self.layout = Layout()
        self.interaction = Interaction()
        self.configure = Configure()
        self.physics = Physics()
        self.edges = EdgeOptions()

    def set(self, new_options):
        options = new_options.replace("\n", "").replace(" ", "")
        first_bracket = options.find("{")
        options = options[first_bracket:]
        options = json.loads(options)
        return options

    def to_json(self):
        return json.dumps(
            self, default=lambda o: o.__dict__,
            sort_keys=True, indent=4)




class Network(object):
    def __init__(self,
                 height="600px",
                 width="100%",
                 ifplot=False,
                 directed=False,
                 bgcolor="#ffffff",
                 keywords_nodes = [],
                 node_color="#FF0000",
                 keyword_color = "#FF0000",
                 font_color=False,
                 font_size=10,
                 edge_width=1,
                 node_size=40,
                 key_weight=1.5,
                 layout=None,
                 heading="ASASDASDAD",
                 ):

        self.ifplot = ifplot
        self.nodes = []
        self.edges = []
        self.height = height
        self.width = width
        self.heading = heading
        self.html = ""
        self.shape = "dot"
        self.keywords_nodes = keywords_nodes
        self.font_color = font_color
        self.node_color = node_color
        self.keyword_color = keyword_color
        self.font_size = font_size
        self.key_weight = key_weight
        self.edge_width = edge_width
        self.node_size = node_size
        self.directed = directed
        self.bgcolor = bgcolor

        self.options = Options(layout)
        self.node_ids = []
        self.node_map = {}
        self.conf = False
        self.path = "template.html"
        self.template_dir = os.path.dirname(__file__) + "/vis_graph/templates/"
        self.templateEnv = Environment(loader=FileSystemLoader(self.template_dir))

    def __str__(self):
        return str(
            json.dumps(
                {
                    "Nodes": self.node_ids,
                    "Edges": self.edges,
                    "Height": self.height,
                    "Width": self.width,
                    "Heading": self.heading
                },
                indent=4
            )
        )

    def add_node(self, n_id, label=None, shape="dot", color="#FF0000", **options):
        assert isinstance(n_id, str) or isinstance(n_id, int)
        if label: node_label = label
        else: node_label = n_id

        keywords_nodes = self.keywords_nodes 
        if n_id not in self.node_ids:
            if n_id in keywords_nodes: 
                node_color = self.keyword_color
                node_size = self.node_size*1.2
                font_size = self.font_size*self.key_weight
            else:
                node_color = self.node_color
                node_size = self.node_size*0.9
                font_size = self.font_size*0.9

            n = Node(n_id, shape, label=node_label, color=node_color, node_size=node_size, font_color=self.font_color, font_size=font_size, **options)

            self.nodes.append(n.options)
            self.node_ids.append(n_id)
            self.node_map[n_id] = n.options

    def add_nodes(self, nodes, **kwargs):
        valid_args = ["size", "value", "title", "x", "y", "label", "color", "shape"]
        for k in kwargs:
            assert k in valid_args, "invalid arg '" + k + "'"

        nd = defaultdict(dict)
        for i in range(len(nodes)):
            for k, v in kwargs.items():
                assert (
                        len(v) == len(nodes)
                ), "keyword arg %s [length %s] does not match" "[length %s] of nodes" % \
                   (
                       k, len(v), len(nodes)
                   )
                nd[nodes[i]].update({k: v[i]})

        for node in nodes:
            # check if node is `number-like`
            try:
                node = int(node)
                self.add_node(node, **nd[node])
            except:
                # or node could be string
                assert isinstance(node, str)
                self.add_node(node, **nd[node])

    def add_edge(self, source, to, **options):
        edge_exists = False
        # verify nodes exists
        assert source in self.get_nodes(), "non existent node '" + str(source) + "'"
        assert to in self.get_nodes(), "non existent node '" + str(to) + "'"

        # we only check existing edge for undirected graphs
        if not self.directed:
            for e in self.edges:
                frm, dest = e['from'], e['to']
                if ( (source == dest and to == frm) or (source == frm and to == dest) ):
                    # edge already exists
                    edge_exists = True

        if not edge_exists:
            e = Edge(source, to, self.directed, edge_width=self.edge_width,**options)
            self.edges.append(e.options)

    def get_network_data(self):
        if isinstance(self.options, dict):
            return (self.nodes, self.edges, self.heading, self.height, self.width, json.dumps(self.options))
        else:
            return (self.nodes, self.edges, self.heading, self.height, self.width, self.options.to_json())

    def save_graph(self, name):
        check_html(name)
        self.write_html(name)

    def generate_html(self, name="index.html"):
        check_html(name)
        use_link_template = False
        for n in self.nodes:
            title = n.get("title", None)
            if title:
                if "href" in title:
                    use_link_template = True
                    break

        template = self.templateEnv.get_template(self.path)  # Template(content)

        nodes, edges, heading, height, width, options = self.get_network_data()

        self.html = template.render(height=height,
                                    width=width,
                                    nodes=nodes,
                                    edges=edges,
                                    heading=heading,
                                    options=options,
                                    bgcolor=self.bgcolor,
                                    ifplot=self.ifplot,
                                    )
        return self.html

    def write_html(self, name):
        local=True
        getcwd_name = name
        check_html(getcwd_name)
        # print(getcwd_name)
        self.html = self.generate_html()
        if not os.path.exists("lib"):
            os.makedirs("lib")
        if not os.path.exists(os.getcwd()+"/lib/vis-9.1.2"):
            shutil.copytree(f"{os.path.dirname(__file__)}/vis_graph/templates/lib/vis-9.1.2", "lib/vis-9.1.2")
        with open(getcwd_name, "w+") as out:
            out.write(self.html)

    def from_nx(self, nx_graph, node_size_transf=(lambda x: x), edge_weight_transf=(lambda x: x),default_node_size =20, default_edge_weight=2, show_edge_weights=True, edge_scaling=False):

        assert(isinstance(nx_graph, nx.Graph))
        edges=nx_graph.edges(data = True)
        nodes=nx_graph.nodes(data = True)

        default_node_size = self.node_size
        default_edge_weight = self.edge_width

        if len(edges) > 0:
            for e in edges:
                if 'size' not in nodes[e[0]].keys():
                    nodes[e[0]]['size']=default_node_size
                nodes[e[0]]['size']=int(node_size_transf(nodes[e[0]]['size']))
                if 'size' not in nodes[e[1]].keys():
                    nodes[e[1]]['size']=default_node_size
                nodes[e[1]]['size']=int(node_size_transf(nodes[e[1]]['size']))
                self.add_node(e[0], **nodes[e[0]])
                self.add_node(e[1], **nodes[e[1]])

                # if user does not pass a 'weight' argument
                if "value" not in e[2] or "width" not in e[2]:
                    if edge_scaling:
                        width_type = 'value'
                    else:
                        width_type = 'width'
                    if "weight" not in e[2].keys():
                        e[2]["weight"] = default_edge_weight
                    e[2][width_type] = edge_weight_transf(e[2]["weight"])
                    # replace provided weight value and pass to 'value' or 'width'
                    e[2][width_type] = e[2].pop("weight")
                self.add_edge(e[0], e[1], **e[2])

        for node in nx.isolates(nx_graph):
            if 'size' not in nodes[node].keys():
                nodes[node]['size'] = default_node_size
            self.add_node(node, **nodes[node])

    def get_nodes(self):
        return self.node_ids

    def get_node(self, n_id):
        return self.node_map[n_id]

    def get_edges(self):
        return self.edges

    def barnes_hut( self, gravity=-80000, central_gravity=0.3, spring_length=250, spring_strength=0.001, damping=0.09, overlap=0):
        self.options.physics.use_barnes_hut(locals())

    def to_json(self, max_depth=1, **args):
        return jsonpickle.encode(self, max_depth=max_depth, **args)
