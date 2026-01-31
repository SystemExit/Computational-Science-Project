import networkx as nx
import random
import sys
import math
from create_sexual_network import create_sexual_network

class NetworkModel():
    """
    Model to simulate HIV spread in a sexual network.

    Args:
        seed: ------------- Seed used in the model
        network_seed: ----- Seed used in the network which the model calls on
        num_node: --------- Number of nodes of the network
        initial_outbreak_proportion: -- Proportion of people in the network starting with HIV
        virus_spread_msm: - Probability of a male infecting another male with hiv
        virus_spread_msf: - Probability of a male infecting a female with hiv
        virus_spread_fsm: - Probability of a female infecting a male with hiv
        virus_spread_fsf: - Probability of a female infecting another female with hiv
        prep_multiplier: -- Proportion of infection probability left when taking PrEP
        art_multiplier: --- Proportion of infection probability left when taking ART
        acute_multiplier: - How much larger the infection probability is when infected person is in the acute stage
        aids_multiplier: -- How much larger the infection probability is when infected person has aids
        acute_to_chronic: - Amount of weeks after infection until chronic state is reached
        infection_to_aids:- Amount of weeks after infection until aids state is reached
        mode: ------------- Which group of people initially takes PrEP (none, random or targeted)
        prep_amount: ------ Proportion of the target group (specofied in 'mode') initially taking PrEP
        check_frequencies:  Dictionary of probabilities of checking for HIV per week, per sexual class
        condom_usage: ----- Probability of using a condom per sexual act, per sexuality
        condom_efficacy: -- Proportion of infection probability left when using condoms, per sexuality
    """
    def __init__(
        self,
        seed:int|None = None,
        network_seed = 67,
        num_nodes:int = 1000,
        initial_outbreak_proportion:int = 0.01,
        virus_spread_msm:float = 1.49/100,
        virus_spread_msf:float = 0.08/100,
        virus_spread_fsm:float = 0.04/100,
        virus_spread_fsf:float = 0.0/100,
        prep_multiplier:float = 0.14,
        art_multiplier:float = 0.04,
        acute_multiplier:int = 26,
        aids_multiplier:int = 7,
        acute_to_chronic:int = 12,
        infection_to_aids = 52*8.5,
        mode:str = "standard",
        prep_amount:float = 0.3,
        check_frequencies = {
            "female homosexual": 0.0,
            "male homosexual": 0.02,
            "female heterosexual": 0.004,
            "male heterosexual": 0.004,
            "female bisexual": 0.004,
            "male bisexual": 0.02,
        },
        condom_usage = {'male-male': 0.258, 'male-female': 0.200, 
                        'female-male': 0.200, 'female-female': 0.0},
        condom_efficacy = {'male-male': 0.25, 'male-female': 0.20, 
                            'female-male': 0.20, 'female-female': 0.0},
    ):

        self.seed = seed
        self.infection_chances = {'male-male': virus_spread_msm, 'male-female': virus_spread_msf, 
                                  'female-male': virus_spread_fsm, 'female-female': virus_spread_fsf}
        self.infection_multipliers = {'acute': acute_multiplier, 'chronic': 1, 'aids': aids_multiplier}
        self.intervention_multipliers = {'prep': prep_multiplier, 'art': art_multiplier, 'none': 1}
        self.check_frequencies = check_frequencies
        self.condom_usage = condom_usage
        self.condom_efficacy = condom_efficacy
        self.acute_to_chronic = acute_to_chronic
        self.infection_to_aids = infection_to_aids
        self.rng = random.Random(seed)
        self.states_per_time: list[dict[str, int]] = []
        self.mode = mode
        self.prep_amount = prep_amount

        #create initial graph
        self.graph = create_sexual_network(N=num_nodes, seed=network_seed, pr_infected_initial=initial_outbreak_proportion)
        for node in self.graph.nodes():
            self.graph.nodes[node]["intervention"] = 'none' #PrEP or ART

        self.prep_intake()
        self.states_per_time.append(self.count_states())


    def prep_intake(self) -> None:
        """
        Make an initial group of people take PrEP, based on the mode parameter.
        """
        prep_dict = {"targeted_m_homo": ["male homosexual"], "targeted_m_hetero": ["male heterosexual"], "targeted_m_bi": ["male bisexual"], 
                    "targeted_f_homo": ["female homosexual"], "targeted_f_hetero": ["female heterosexual"], "targeted_f_bi": ["female bisexual"],
                    "targeted_male": ["male homosexual", "male heterosexual", "male bisexual"], "targeted_female": ["female homosexual", "female heterosexual", "female bisexual"],
                    "targeted_homosexual": ["male homosexual", "female homosexual"], "targeted_heterosexual": ["male heterosexual", "female heterosexual"],
                    "targeted_bisexual": ["male bisexual", "female bisexual"]}

        if self.mode == "standard":
            pass
        elif self.mode == "random":
                sus = [node for node in self.graph.nodes() if self.graph.nodes[node]['state'] == 'susceptible']
                random_prep = self.rng.sample(sus, int(self.prep_amount * len(sus)))
                for node in random_prep:
                    self.graph.nodes[node]["intervention"] = "prep" 
        else:
            target = [node for node in self.graph.nodes() if self.graph.nodes[node]['state'] == 'susceptible' and self.graph.nodes[node]['klasse'] in prep_dict[self.mode]]
            random_prep = self.rng.sample(target, int(self.prep_amount * len(target))) 
            for node in random_prep:
                self.graph.nodes[node]["intervention"] = "prep"
        
    def intervention_intake(self, node:int, state: str, timer: int) -> None:
        klasse = self.graph.nodes[node]["klasse"]
        if state == "susceptible":
            # take prep if at least two neighbors take prep (realistically, only male homosexuals / male bisexuals do this)
            count = sum([1 for n in self.graph.neighbors(node) if self.graph.nodes[n]["intervention"] == "prep"])
            if count >= 2 and klasse == 'male homosexual':
                if self.rng.random() < 0.1:
                    self.graph.nodes[node]["intervention"] = "prep"
            elif count >= 2 and klasse == 'male bisexual':
                if self.rng.random() < 0.05:
                    self.graph.nodes[node]["intervention"] = "prep"
        elif state in ["acute","chronic"] and self.graph.nodes[node]["intervention"] != "art":
            art_prob = self.check_frequencies[klasse] # probability of going for a check-in
            if timer > 6: #people eventually start to notice they have symptoms
                art_prob += 0.0025
            if self.rng.random() < art_prob:
                self.graph.nodes[node]["intervention"] = "art"
        elif state == "aids":
                self.graph.nodes[node]["intervention"] = "art"
            
    
    def count_states(self) -> dict[str, int]:
        """
        Keep track of the current state of the network.
        Returns dictionary with all current states and klasses of infected people.

        >>> model = NetworkModel()
        >>> nodes = [(0, {'state': 'susceptible', 'gender': 'male', 'klasse':'male homosexual', 'intervention': 'none'}), 
        ... (1, {'state': 'susceptible', 'gender': 'male', 'klasse':'male heterosexual', 'intervention': 'none'}), 
        ... (2, {'state': 'susceptible', 'gender': 'female', 'klasse':'female heterosexual', 'intervention': 'none'}),
        ... (3, {'state': 'susceptible', 'gender': 'male', 'klasse':'male homosexual', 'intervention': 'none'}), ]
        >>> edges = [(0, 3), (1, 2)]
        >>> G = nx.Graph(); G.add_nodes_from(nodes); G.add_edges_from(edges)
        >>> model.graph = G
        >>> model.count_states()
        {'susceptible': 4, 'acute': 0, 'chronic': 0, 'aids': 0, 'dead': 0, 'male homosexual': 0, 'male heterosexual': 0, 'male bisexual': 0, 'female homosexual': 0, 'female heterosexual': 0, 'female bisexual': 0, 'prep': 0, 'art': 0}

        >>> nodes = [(0, {'state': 'acute', 'gender': 'male', 'klasse':'male homosexual', 'intervention': 'none'}), 
        ... (1, {'state': 'susceptible', 'gender': 'male', 'klasse':'male heterosexual', 'intervention': 'none'}), 
        ... (2, {'state': 'susceptible', 'gender': 'female', 'klasse':'female heterosexual', 'intervention': 'none'}),
        ... (3, {'state': 'susceptible', 'gender': 'male', 'klasse':'male homosexual', 'intervention': 'none'}), ]
        >>> edges = [(0, 3), (1, 2)]
        >>> G = nx.Graph(); G.add_nodes_from(nodes); G.add_edges_from(edges)
        >>> model.graph = G
        >>> model.count_states()
        {'susceptible': 3, 'acute': 1, 'chronic': 0, 'aids': 0, 'dead': 0, 'male homosexual': 1, 'male heterosexual': 0, 'male bisexual': 0, 'female homosexual': 0, 'female heterosexual': 0, 'female bisexual': 0, 'prep': 0, 'art': 0}

        >>> nodes = [(0, {'state': 'acute', 'gender': 'male', 'klasse':'male homosexual', 'intervention': 'none'}), 
        ... (1, {'state': 'acute', 'gender': 'male', 'klasse':'male heterosexual', 'intervention': 'none'}), 
        ... (2, {'state': 'chronic', 'gender': 'female', 'klasse':'female heterosexual', 'intervention': 'none'}),
        ... (3, {'state': 'aids', 'gender': 'male', 'klasse':'male homosexual', 'intervention': 'none'}), ]
        >>> edges = [(0, 3), (1, 2)]
        >>> G = nx.Graph(); G.add_nodes_from(nodes); G.add_edges_from(edges)
        >>> model.graph = G
        >>> model.count_states()
        {'susceptible': 0, 'acute': 2, 'chronic': 1, 'aids': 1, 'dead': 0, 'male homosexual': 2, 'male heterosexual': 1, 'male bisexual': 0, 'female homosexual': 0, 'female heterosexual': 1, 'female bisexual': 0, 'prep': 0, 'art': 0}
        """
        
        count_dict = {'susceptible': 0, 'acute': 0, 'chronic': 0, 'aids': 0, 'dead': 0,
                      'male homosexual': 0, 'male heterosexual': 0, 'male bisexual': 0, 
                      'female homosexual': 0, 'female heterosexual': 0, 'female bisexual': 0,
                      'prep': 0, 'art': 0}
        for node in self.graph.nodes():
            #state
            state = self.graph.nodes[node]['state']
            count_dict[state] += 1

            #intervention
            intervention = self.graph.nodes[node]['intervention']
            if intervention != "none":
                count_dict[intervention] += 1

            #infected classes
            klasse = self.graph.nodes[node]['klasse']
            if state in ['acute', 'chronic', 'aids']:
                count_dict[klasse] += 1
            
        return count_dict
    
    def count_classes(self) -> dict[str, int]:
        """
        Count the number of people per class in the network of the model
        """
        class_dict = {"male homosexual": 0, "male heterosexual": 0, "male bisexual": 0,
                      "female homosexual": 0, "female heterosexual": 0, "female bisexual": 0, 
                      'heterosexual': 0, 'homosexual': 0, 'bisexual': 0, 'male': 0, 'female': 0}
        homosexual = ["male homosexual", "female homosexual"] 
        heterosexual = ["male heterosexual", "female heterosexual"] 
        bisexual = ["male bisexual", "female bisexual"]        

        for node in self.graph.nodes():
            klasse = self.graph.nodes[node]['klasse']
            class_dict[klasse] += 1
            gender = self.graph.nodes[node]['gender']
            class_dict[gender] += 1

            if klasse in homosexual:
                class_dict['homosexual'] += 1
            elif klasse in heterosexual:
                class_dict['heterosexual'] += 1
            elif klasse in bisexual:
                class_dict['bisexual'] += 1
        return class_dict
        

    def sexual_act(self, node1:int, node2:int, weight:float|None) -> None:
        """
        Perform a sexual act and possibly infect sexual partner.

        >>> states = []
        >>> for _ in range(10):
        ...    model = NetworkModel(num_nodes = 2, initial_outbreak_proportion=0.5, virus_spread_msm=1, virus_spread_msf=1, virus_spread_fsm=1, virus_spread_fsf = 1)
        ...    model.condom_usage = {'male-male': 0.0, 'male-female': 0.0, 'female-male': 0.0, 'female-female': 0.0}
        ...    model.sexual_act(0, 1, 1)
        ...    state1, state2 = model.graph.nodes[0]['state'], model.graph.nodes[1]['state']
        ...    states.append(state1 == 'acute' and state2 == 'acute')
        >>> round(sum(states) / len(states), 3) == 1
        True
        >>> states = []
        >>> for _ in range(10):
        ...    model = NetworkModel(num_nodes = 2, initial_outbreak_proportion=0.0, virus_spread_msm=1, virus_spread_msf=1, virus_spread_fsm=1, virus_spread_fsf = 1)
        ...    model.sexual_act(0, 1, 1)
        ...    state1, state2 = model.graph.nodes[0]['state'], model.graph.nodes[1]['state']
        ...    states.append(state1 == 'susceptible' and state2 == 'susceptible')
        >>> round(sum(states) / len(states), 3) == 1
        True
        >>> states = []
        >>> for _ in range(10):
        ...    model = NetworkModel(num_nodes = 2, initial_outbreak_proportion=0.5)
        ...    model.sexual_act(0, 1, 0)
        ...    state1, state2 = model.graph.nodes[0]['state'], model.graph.nodes[1]['state']
        ...    states.append((state1 == 'acute' and state2 == 'susceptible') or (state1 == 'susceptible' and state2 == 'acute'))
        >>> round(sum(states) / len(states), 3) == 1
        True
        >>> states = []
        >>> for _ in range(10):
        ...    model = NetworkModel(num_nodes = 2, initial_outbreak_proportion=0.5, virus_spread_msm=0, virus_spread_msf=0, virus_spread_fsm=0, virus_spread_fsf=0)
        ...    model.sexual_act(0, 1, 1)
        ...    state1, state2 = model.graph.nodes[0]['state'], model.graph.nodes[1]['state']
        ...    states.append((state1 == 'acute' and state2 == 'susceptible') or (state1 == 'susceptible' and state2 == 'acute'))
        >>> round(sum(states) / len(states), 3) == 1
        True
        """
        state1 = self.graph.nodes[node1]["state"]
        state2 = self.graph.nodes[node2]["state"]
        intervention1 = self.graph.nodes[node1]["intervention"]
        intervention2 = self.graph.nodes[node2]["intervention"]
        gender1 = self.graph.nodes[node1]["gender"]
        gender2 = self.graph.nodes[node2]["gender"]
        weight = weight if weight else 0.2 

        if self.rng.random() < weight: # sexual act takes place
            if state1 != "susceptible" and state2 == "susceptible":
                infection_chance = self.infection_chances[f"{gender1}-{gender2}"]
                infection_chance *= self.infection_multipliers[state1]
                infection_chance *= self.intervention_multipliers[intervention1] * self.intervention_multipliers[intervention2]
                if self.rng.random() < self.condom_usage[f"{gender1}-{gender2}"]: #condom use
                    infection_chance *= self.condom_efficacy[f"{gender1}-{gender2}"]

                if self.rng.random() < infection_chance: # infection takes place
                    self.graph.nodes[node2]["state"] = "acute"
                    self.graph.nodes[node2]["intervention"] = "none" # prep does not work anymore if you're infected
            elif state2 != "susceptible" and state1 == "susceptible":
                infection_chance = self.infection_chances[f"{gender2}-{gender1}"] 
                infection_chance *= self.infection_multipliers[state2]
                infection_chance *= self.intervention_multipliers[intervention1] * self.intervention_multipliers[intervention2]
                if self.rng.random() < self.condom_usage[f"{gender1}-{gender2}"]: #condom use
                    infection_chance *= self.condom_efficacy[f"{gender1}-{gender2}"] 

                if self.rng.random() < infection_chance: # infection takes place
                    self.graph.nodes[node1]["state"] = "acute"
                    self.graph.nodes[node1]["intervention"] = "none" # prep does not work anymore if you're infected

    

    def step(self) -> None:
        # change state from | acute-->chronic | chronic-->aids | aids-->dead | after a certain time/probability
        for node in self.graph.nodes():
            state = self.graph.nodes[node]["state"]
            timer = self.graph.nodes[node]["infection_time"]
            intervention = self.graph.nodes[node]["intervention"]
            if state == "acute" and timer > self.acute_to_chronic:
                self.graph.nodes[node]["state"] = "chronic"
            elif state == "chronic" and timer > self.infection_to_aids and intervention == 'none':
                self.graph.nodes[node]["state"] = "aids"
            elif state == "aids":
                aids_time = timer - self.infection_to_aids
                if aids_time % 52 == 0: # only check death once a year:
                    aids_years = aids_time / 52
                    death_rate = (1 - (0.9182 * math.exp(-0.29*aids_years)))

                    if self.rng.random() < death_rate:
                        self.graph.nodes[node]["state"] = "dead"
            
            self.intervention_intake(node, state, timer) #possibility of art or prep
        
                
        # possibly perform a sexual act 
        edges = list(self.graph.edges(data=True))
        self.rng.shuffle(edges)
        for node1, node2, data in edges:
            weight = data['weight'] if data else None
            if self.graph.nodes[node1]["state"] != "dead" and self.graph.nodes[node2]["state"] != "dead":
                self.sexual_act(node1, node2, weight)

        # update infection time
        for node in self.graph.nodes():
             if self.graph.nodes[node]["state"] in ["acute", "chronic", "aids"]:
                  self.graph.nodes[node]["infection_time"] += 1
        
        # update state counts
        self.states_per_time.append(self.count_states())



if __name__ == '__main__':
    if len(sys.argv) < 2:
        mode = "standard"
    else:
        mode = sys.argv[1]

    modes = ["standard", "random", "targeted_m_homo", "targeted_m_hetero", "targeted_m_bi", 
             "targeted_f_homo", "targeted_f_hetero", "targeted_f_bi", "targeted_homosexual", 
             "targeted_heterosexual", "targeted_bisexual", "targeted_male", "targeted_female"]

    if mode not in modes:
        print(f"Unknown mode: {mode} not in {str(modes)}")
        sys.exit(1)

    print(f'Creating model with mode {mode}')
    model = NetworkModel(mode = mode) 

    print('Class proportions in network:')
    print(model.count_classes())
    print('Running model...')
    for t in range(520):
        model.step()
    print('Model states after 520 weeks (10 years)')
    print(model.count_states())






