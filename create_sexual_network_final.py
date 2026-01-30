import networkx as nx
import random
import math
import csv

def sexual_frequency(G:nx.Graph) -> nx.Graph:
    """
    Add probabilities of having sex per week as weights to all edged of G.
    """
    #average amount of sex per week per class
    sexual_frequencies = { 
            "male homosexual": 2.25,
            "male heterosexual": 1.65,
            "male bisexual": 2.25,
            "female homosexual": 1.25,
            "female heterosexual": 1.65,
            "female bisexual": 1.65,
        }
    
    # calculate average sexual probability per node-neighbour relation
    freq_per_edge = {}
    for node in G.nodes():
        klasse = G.nodes[node]['klasse']
        freq_per_neighbour = sexual_frequencies[klasse] / len(list(G.neighbors(node)))
        freq_per_edge[node] = freq_per_neighbour
    
    # update weight for each edge as average probability of both nodes
    for (n1, n2) in G.edges():
        G[n1][n2]["weight"] = (freq_per_edge[n1] + freq_per_edge[n2]) / 2 
    
    return G

def create_sexual_network(N=1000, pr_infected_initial=0.01, seed=None, pr_male_heterosexual=0.50*0.900, pr_male_homosexual=0.50*0.049, pr_male_bisexual=0.50*0.051,
                          pr_female_heterosexual=0.50*0.907, pr_female_homosexual=0.50*0.021, pr_female_bisexual=0.50*0.072,
                          data_file_name="22140-0002-Data.tsv"):
    """returns a networkx graph that represents a sexual network of N nodes, where each node (female/male) has at least one edge (sexual relationship) with another node. 
    Each node is sorted into one of the six classes: male homosexual/male heterosexual/male bisexual/female homosexual/female heterosexual/female bisexual, and its 
    degree is determined by sampling from the degree distribution of the nodes of that class in the network formed by the egodyads dataset (Morris & Rothenberg, 2011).
    All nodes in the networkx graph are labeled with the class ("klasse"), gender ("gender") and HIV status ("HIV_status") attribute. After creaing the simulated sexual network, a portion of 
    the population is infected with HIV, according to the parameter pr_infected_initial and the proportion of nodes that are infected in each class in Egodyads network. 

    :N:                         amount of agents in the simulated sexual network
    :pr_infected_initial:       proportion of agents that are infected in the simulated sexual network
    :seed:                      initialisation of random number generator
    :pr_male_homosexual:        proportion of agents in that are male and have intercourse only with males
    :pr_male_heterosexual:      proportion of agents that are male and have intercourse only with females
    :pr_male_bisexual:          proportion of agents that are male and have intercourse with females and males
    :pr_female_homosexual:      proportion of agents in that are female and have intercourse only with females
    :pr_female_heterosexual:    proportion of agents that are female and have intercourse only with males
    :pr_female_bisexual:        proportion of agents that are female and have intercourse with females and males
    :data_file_name:            file name of the egodyads dataset   

    Default parameters for sexual parameters have been extracted from reported sexual identity accross 28 nations, see Table 4. Rahman, Q., Xu, Y., Lippa, R. A., & Vasey, P. 
    L. (2020). Prevalence of Sexual Orientation Across 28 Nations and Its Association with Gender Equality, Economic Development, and Individualism. Archives of sexual 
    behavior, 49(2), 595–606.

    Only genders male and female, and sexual relationships between these genders have been considered for creating the network, due to limited data availability. 
    The proportion of males is assumed to be equal to the proportion of females.
    """

    # Load in the egodyads dataset from Morris, M., & Rothenberg, R. (2011). HIV transmission network metastudy project: An archive of data from eight network studies, 
    # 1988--2001. An egodyad is a relation (edge) reported by the respondent (ego) that is between the respondent and someone the respondent knows, as opposed to an
    # altdyad which is defined as a relationship reported by the ego that is between two other people (alters) the respondent knows; see Wasserman, S. (1994). 
    # Social network analysis: Methods and applications. page 42. The egodyads dataset is used for construction of a new sexual network instead of the altdyads dataset, 
    # because it is more accurate; egos know for certain all their relationships with alters, whilst egos might not know all the relationships between their alters.

    # # # 1. Determine the male/female degree and class (one of the six) of each node.
    edge_list = []
    HIV_positive = list() # List of tuples: (node_1, node_2, sex_node_1, sex_node_2)
    # where node_1 is in the sexual network who were tested for HIV and tested positive.   
    genders = dict() # Gender of each node
    
    with open(data_file_name, 'r') as csv_file:
        reader = csv.DictReader(csv_file, delimiter="\t")
        for row in reader:
            tietype = row["TIETYPE"] # mode of connection of ego with alter 1: social, 2: drug,  3: sexual, 4: needle
            ego_gender = row["SEX1"]
            alter_gender = row["SEX2"]
            gender_def = {
                            "0": "male",
                            "1": "female"
                          }
            infected = row["HIV1"]
            # Select only data for which the mode of connection between ego and alter was sexual, and both their gender was identified
            if tietype == "3" and ego_gender in gender_def and alter_gender in gender_def: 
                ego, alter = int(row["ID1"]), int(row["ID2"])
                edge_list.append((ego,alter)) # add the edge between the ego and the alter
                # Add the ego and its gender to the genders dictionary
                genders[ego] = gender_def[ego_gender]
                genders[alter] = gender_def[alter_gender]
                if infected == "1":
                    HIV_positive.append((ego,alter,gender_def[ego_gender],gender_def[alter_gender]))
    # Create the egodyads network
    G = nx.Graph(edge_list)

    # Calculate the male and female degree per node of a class and add it to the male/female degree dictionary. Repeat this for each node.
    degrees_per_class = {
        "male homosexual": {"male degree": []}, 
        "male heterosexual": {"female degree": []},
        "male bisexual": {"male degree": [], "female degree": []}, 
        "female homosexual": {"female degree": []}, 
        "female heterosexual": {"male degree": []},
        "female bisexual": {"male degree": [], "female degree": []} 
    }
    for node in G:
        ego_gender = genders[node]
        alters = list(G.neighbors(node))
        male_alters, female_alters = 0, 0
        for alter in alters:
            if genders[alter] == "male":
                male_alters += 1
            else:
                female_alters += 1
        if ego_gender == "male":
            if male_alters > 0 and female_alters > 0:
                degrees_per_class["male bisexual"]["male degree"].append(male_alters)
                degrees_per_class["male bisexual"]["female degree"].append(female_alters)
            elif male_alters > 0:
                degrees_per_class["male homosexual"]["male degree"].append(male_alters)
            elif female_alters > 0:
                degrees_per_class["male heterosexual"]["female degree"].append(female_alters)
        elif ego_gender == "female": 
            if male_alters > 0 and female_alters > 0:
                degrees_per_class["female bisexual"]["male degree"].append(male_alters)
                degrees_per_class["female bisexual"]["female degree"].append(female_alters) 
            elif female_alters > 0:
                degrees_per_class["female homosexual"]["female degree"].append(female_alters)
            elif male_alters > 0: 
                degrees_per_class["female heterosexual"]["male degree"].append(male_alters)
    
    
    # # # 2. Now we create a network of N nodes which first are divided into classes according to the input proportion parameters.
    random.seed(seed)
    proportion_per_class = [
                        pr_male_homosexual, pr_male_heterosexual, pr_male_bisexual, 
                        pr_female_homosexual, pr_female_heterosexual, pr_female_bisexual 
                        ]
    class_and_gender = [
        ('male homosexual','male'), ('male heterosexual','male'), ('male bisexual','male'),
        ('female homosexual', 'female'), ('female heterosexual', 'female'), ('female bisexual', 'female')
        ]
    H = nx.Graph()
    for i in range(N):
        node_class_and_gender = random.choices(class_and_gender, proportion_per_class)[0]
        H.add_node(i, klasse=node_class_and_gender[0])
        H.add_node(i, gender=node_class_and_gender[1])
    # We track to which sexuality and gender (class) the nodes have
    male_homosexual_nodes, male_heterosexual_nodes, male_bisexual_nodes = set(), set(), set()
    female_homosexual_nodes, female_heterosexual_nodes, female_bisexual_nodes = set(), set(), set()
   
    for node in H:
        node_class = H.nodes[node]["klasse"]
        if node_class == "male homosexual":
            male_homosexual_nodes.add(node)
        elif node_class == "male heterosexual":
            male_heterosexual_nodes.add(node)
        elif node_class == "male bisexual":
            male_bisexual_nodes.add(node)
        elif node_class == "female homosexual":
            female_homosexual_nodes.add(node)
        elif node_class == "female heterosexual":
            female_heterosexual_nodes.add(node)
        elif node_class == "female bisexual":
            female_bisexual_nodes.add(node)
     
    # Then we add the connections between the nodes, by sampling from the male and/or female degree list of the class that the node belongs to.
    for node in H:
        node_class = H.nodes[node]["klasse"]
        chosen_alters = []
        # Sample the gender (male/female) degree from the gender degree list in the class dictionary, and add gender degree edges 
        # (minus the edges the node already has) between the node in question and nodes that belong to the potential alters. 
        # The node's degree cannot exceed the size of the set the node belongs to, thus it is defined as follows
        if node_class == "male homosexual":
            potential_alters = list((male_homosexual_nodes | male_bisexual_nodes) - {node} - set(H.neighbors(node)))
            male_degree = min(random.choice(degrees_per_class["male homosexual"]["male degree"]) - H.degree(node), len(potential_alters))
            if male_degree > 0:
                chosen_alters = random.sample(potential_alters, male_degree)

        elif node_class == "male heterosexual":
            potential_alters = list((female_bisexual_nodes | female_heterosexual_nodes) - {node} - set(H.neighbors(node)))
            female_degree = min(random.choice(degrees_per_class["male heterosexual"]["female degree"]) - H.degree(node), len(potential_alters))
            if female_degree > 0:
                chosen_alters = random.sample(potential_alters, female_degree)
            

        elif node_class == "male bisexual":
            potential_male_alters = list(male_bisexual_nodes - {node} - set(H.neighbors(node)))
            potential_female_alters = list((female_bisexual_nodes | female_heterosexual_nodes) - {node} - set(H.neighbors(node)))
            male_degree = min(random.choice(degrees_per_class["male bisexual"]["male degree"]) - H.degree(node), len(potential_male_alters))
            female_degree = min(random.choice(degrees_per_class["male bisexual"]["female degree"]) - H.degree(node), len(potential_female_alters))
            if male_degree > 0 and female_degree <= 0:
                chosen_alters = random.sample(potential_male_alters, male_degree)
            elif female_degree > 0 and male_degree <= 0 :
                chosen_alters = random.sample(potential_female_alters, female_degree)
            elif female_degree > 0 and male_degree > 0:
                chosen_alters = random.sample(potential_male_alters, male_degree) + random.sample(potential_female_alters, female_degree)

        elif node_class == "female homosexual":
            potential_alters = list((female_homosexual_nodes | female_bisexual_nodes) - {node} - set(H.neighbors(node)))
            female_degree = min(random.choice(degrees_per_class["female homosexual"]["female degree"]) - H.degree(node), len(potential_alters))
            if female_degree > 0:
                chosen_alters = random.sample(potential_alters, female_degree)

        elif node_class == "female heterosexual":
            potential_alters = list((male_heterosexual_nodes | male_bisexual_nodes) - {node} - set(H.neighbors(node)))
            male_degree = min(random.choice(degrees_per_class["female heterosexual"]["male degree"]) - H.degree(node), len(potential_alters))
            if male_degree > 0:
                chosen_alters = random.sample(potential_alters, male_degree)

        elif node_class == "female bisexual":
            potential_male_alters = list((male_bisexual_nodes | male_heterosexual_nodes) - {node} - set(H.neighbors(node)))
            potential_female_alters = list(female_bisexual_nodes - {node} - set(H.neighbors(node)))
            male_degree = min(random.choice(degrees_per_class["male bisexual"]["male degree"]) - H.degree(node), len(potential_male_alters))
            female_degree = min(random.choice(degrees_per_class["male bisexual"]["female degree"]) - H.degree(node), len(potential_female_alters))
            if male_degree > 0 and female_degree <= 0:
                chosen_alters = random.sample(potential_male_alters, male_degree)
            elif female_degree > 0 and male_degree <= 0:
                chosen_alters = random.sample(potential_female_alters, female_degree)
            elif female_degree > 0 and male_degree > 0:
                chosen_alters = random.sample(potential_male_alters, male_degree) + random.sample(potential_female_alters, female_degree)

        # Now add the edges between the nodes and its chosen alters
        for chosen_alter in chosen_alters:
            H.add_edge(node, chosen_alter)        
    
    # # # 3. Lastly we simulate infecting an initial part of the population
    
    # Variables concerning nodes in Egodyads network.
    classes = ["male homosexual", "male heterosexual", "male bisexual", "female homosexual", "female heterosexual", "female bisexual"]
    class_and_nodes = {klasse: set() for klasse in classes}
    for node in H:
        node_class = H.nodes[node]["klasse"]
        class_and_nodes[node_class].add(node)
      
    # Variables concerning nodes in Egodyads network that were tested for HIV.
    total_positive = len(HIV_positive)
    pr_infected_per_class = {klasse: 0 for klasse in classes} # proportion of infected nodes that belonged to class klasse
    
    
    # Of the infected nodes we calculate how many belong to each class, so we can calculate the proportion of infected nodes that belong to each class.
    # We determine the class of the node and add one to counter of the class it came from in pr_infected_per_class
    nodes_encountered = set()
    for node_1, _, gender_1, _ in HIV_positive:
        if node_1 in nodes_encountered:
            continue
        nodes_encountered.add(node_1)
        sexuality_list = ["F", "F"] # letter at index 0 indicates if node_1 had sex with male (F: false, T: true),
        # letter at index 1 if node_1 had sex with female (F: false, T: true)
        for ego, _, _, gender_alter in HIV_positive:
            if ego == node_1:
                if gender_alter == "male":
                    sexuality_list[0] = "T"
                elif gender_alter == "female":
                    sexuality_list[1] = "T"
        if gender_1 == "male":
            if sexuality_list == ["T", "T"]:
                pr_infected_per_class["male bisexual"] += 1
            elif sexuality_list == ["T", "F"]:
                pr_infected_per_class["male homosexual"] += 1
            elif sexuality_list == ["F", "T"]:
                pr_infected_per_class["male heterosexual"] += 1
        elif gender_1 == "female":
            if sexuality_list == ["T", "T"]:
                pr_infected_per_class["female bisexual"] += 1  
            elif sexuality_list == ["F", "T"]:
                pr_infected_per_class["female homosexual"] += 1
            elif sexuality_list == ["T", "F"]:
                pr_infected_per_class["female heterosexual"] += 1

    for klasse in classes:
        pr_infected_per_class[klasse] /= total_positive



    # Now we infect nodes according to the proportion of infected per class in the egodyads network
    
    # Variables concerning the simulated network
    # number of nodes that ought to be infected
    total_infected = math.ceil(pr_infected_initial*N) 
    # number of nodes that ought to be infected per class (can't exceed the size of the class)
    total_infected_per_class = {klasse:min(pr_infected_per_class[klasse]*total_infected, len(class_and_nodes[klasse])) for klasse in classes}
    # number of nodes will actually infected per class (must sum up to total_infected, using the following procedure)
    infected_per_class = {klasse: int(total_infected_per_class[klasse]) for klasse in classes} 
   
    # now we rectify the difference between representation specified in total_infected_per_class and assigned representation in infected_per_class, 
    # such that the most underrepresented classes gain more infected, and adding these infected nodes makes the amount infected 
    # equal the amount that ought to be infected
    useful_classes = ["male homosexual", "male heterosexual", "male bisexual", "female homosexual", "female heterosexual", "female bisexual"]
    while sum(list(infected_per_class.values())) < total_infected:
       
        # find the most undderrepresented class
        max_diff = float("-inf")
        most_underrepresented = None

        for klasse in useful_classes:
            if infected_per_class[klasse] == len(class_and_nodes[klasse]):
                useful_classes.remove(klasse)
                continue
            infected_specified = total_infected_per_class[klasse]
            infected_assigned = infected_per_class[klasse]
            difference_in_representation = infected_specified - infected_assigned 
            if difference_in_representation > max_diff:
                max_diff = difference_in_representation
                most_underrepresented = klasse 

        # make that class more represented by adding one to the amount of nodes that will be infected of that class
        infected_per_class[most_underrepresented] += 1

    # Now that we know for each class how many nodes are infected, we infect nodes of that class randomly  
    for klasse in classes:
        total_infected_in_class = infected_per_class[klasse]
        nodes_in_class = list(class_and_nodes[klasse])
        infected_nodes_in_class = random.sample(nodes_in_class, k=total_infected_in_class)   
        for node in infected_nodes_in_class:
            H.nodes[node]['state'] = "acute"
            H.nodes[node]["infection_time"] = 1
        uninfected_nodes_in_class = list(set(nodes_in_class) - set(infected_nodes_in_class))
        for node in uninfected_nodes_in_class:
            H.nodes[node]['state'] = "susceptible"
            H.nodes[node]["infection_time"] = 0
    
    # add weights
    H = sexual_frequency(H)

    return H


if __name__ == '__main__':
    #test correctness of sexual links 
    valid = True
    for _ in range(100):
        G = create_sexual_network(N=1000, seed=None)
        error1, error2, error3, error4, error5, error6 = None, None, None, None, None, None
        error7, error8, error9, error10, error11, error12 = None, None, None, None, None, None
        f_homo_count, m_homo_count = 0, 0
        f_hetero_count, m_hetero_count = 0, 0
        f_bi_count, m_bi_count = 0, 0

        for node in G.nodes():
            klasse = G.nodes[node]['klasse']
            gender = G.nodes[node]['gender']
            neighbors = list(G.neighbors(node))
            if klasse == 'female homosexual':
                f_homo_count += 1
                if not all(G.nodes[neighbor]['klasse'] == 'female homosexual' or G.nodes[neighbor]['klasse'] == 'female bisexual' 
                    for neighbor in neighbors):
                    if any(G.nodes[neighbor]['gender'] == 'male' for neighbor in neighbors):
                        if not error1:
                            print('Some gay women have sex with men')
                            error1 = True
                    if any(G.nodes[neighbor]['klasse'] == 'female heterosexual' for neighbor in neighbors):
                        if not error2:
                            print('Some gay women have sex with heterosexual women')
                            error2 = True
                    valid = False
                    
            elif klasse == 'male homosexual':
                m_homo_count += 1
                if not all(G.nodes[neighbor]['klasse'] == 'male homosexual' or G.nodes[neighbor]['klasse'] == 'male bisexual' 
                    for neighbor in neighbors):
                    if any(G.nodes[neighbor]['gender'] == 'female' for neighbor in neighbors):
                        if not error3:
                            print('Some gay men have sex with women')
                            error3 = True
                    if any(G.nodes[neighbor]['klasse'] == 'male heterosexual' for neighbor in neighbors):
                        if not error4:
                            print('Some gay men have sex with heterosexual men')
                            error4 = True
                    valid = False
                    
            elif klasse == 'female heterosexual':
                f_hetero_count += 1
                if not all(G.nodes[neighbor]['klasse'] == 'male heterosexual' or G.nodes[neighbor]['klasse'] == 'male bisexual' 
                    for neighbor in neighbors):
                    if any(G.nodes[neighbor]['gender'] == 'female' for neighbor in neighbors):
                        if not error5:
                            print('Some heterosexual women have sex with women')
                            error5 = True
                    if any(G.nodes[neighbor]['klasse'] == 'male homosexual' for neighbor in neighbors):
                        if not error6:
                            print('Some heterosexual women have sex with gay men')
                            error6 = True
                    valid = False
                    
            elif klasse == 'male heterosexual':
                m_hetero_count += 1
                if not all(G.nodes[neighbor]['klasse'] == 'female heterosexual' or G.nodes[neighbor]['klasse'] == 'female bisexual' 
                    for neighbor in neighbors):
                    if any(G.nodes[neighbor]['gender'] == 'male' for neighbor in neighbors):
                        if not error7:
                            print('Some heterosexual men have sex with men')
                            error7 = True
                    if any(G.nodes[neighbor]['klasse'] == 'female homosexual' for neighbor in neighbors):
                        if not error8:
                            print('Some heterosexual men have sex with gay women')
                            error8 = True
                    valid = False
                    
            elif klasse == 'female bisexual':
                f_bi_count += 1
                if not all(G.nodes[neighbor]['klasse'] == 'male heterosexual' or G.nodes[neighbor]['klasse'] == 'male bisexual' or 
                        G.nodes[neighbor]['klasse'] == 'female homosexual' or G.nodes[neighbor]['klasse'] == 'female bisexual'
                        for neighbor in neighbors):
                    if any(G.nodes[neighbor]['klasse'] == 'female heterosexual' for neighbor in neighbors):
                        if not error9:
                            print('Some bisexual women have sex with heterosexual women')
                            error9=True
                    if any(G.nodes[neighbor]['klasse'] == 'male homosexual' for neighbor in neighbors):
                        if not error10:
                            print('Some bisexual women have sex with gay men')
                            error10 = True
                    valid = False
                    
            elif klasse == 'male bisexual':
                m_bi_count += 1
                if not all(G.nodes[neighbor]['klasse'] == 'female heterosexual' or G.nodes[neighbor]['klasse'] == 'female bisexual' or
                        G.nodes[neighbor]['klasse'] == 'male homosexual' or G.nodes[neighbor]['klasse'] == 'male bisexual'
                        for neighbor in neighbors):
                    if any(G.nodes[neighbor]['klasse'] == 'male heterosexual' for neighbor in neighbors):
                        if not error11:
                            print('Some bisexual men have sex with heterosexual men')
                            error11 = True
                    if any(G.nodes[neighbor]['klasse'] == 'female homosexual' for neighbor in neighbors):
                        if not error12:
                            print('Some bisexual men have sex with gay women')
                            error12 = True
                    valid = False
                

    print(f'Test 1: Network is valid: {valid}')
    # print(f'female homo:  {f_homo_count/1000}    --   {0.50*0.021}')
    # print(f'male homo:    {m_homo_count/1000}    --   {0.50*0.049}')
    # print(f'female hetero:{f_hetero_count/1000}   --   {0.50*0.907}')
    # print(f'male hetero:  {m_hetero_count/1000}   --   {0.50*0.900}')
    # print(f'female bi:    {f_bi_count/1000}   --   {0.50*0.072}')
    # print(f'male bi:      {m_bi_count/1000}   --   {0.50*0.051}')


    #################
    f_ho, m_ho = 0.0, 0/0
    f_he, m_he = 0.0, 0.0
    f_bi, m_bi = 0.0, 0.0
    gender_error, klasse_error = None, None

    for _ in range(100):
        G = create_sexual_network(N=1000, seed=None)

        ## Test 2
        f_ho += sum([1 for node in G.nodes() if G.nodes[node]['klasse'] == 'female homosexual']) / 1000
        m_ho += sum([1 for node in G.nodes() if G.nodes[node]['klasse'] == 'male homosexual']) / 1000
        f_he += sum([1 for node in G.nodes() if G.nodes[node]['klasse'] == 'female heterosexual']) / 1000
        m_he += sum([1 for node in G.nodes() if G.nodes[node]['klasse'] == 'male heterosexual']) / 1000
        f_bi += sum([1 for node in G.nodes() if G.nodes[node]['klasse'] == 'female bisexual']) / 1000
        m_bi += sum([1 for node in G.nodes() if G.nodes[node]['klasse'] == 'male bisexual']) / 1000

        ## Test 3
        for node in G.nodes():
            gender = G.nodes[node]['gender']
            klasse = G.nodes[node]['klasse']
            if gender not in ['male', 'female'] and not gender_error:
                gender_error = True
                print(f"Gender {gender} not one of the expected values: ['male', 'female']")   
            if klasse not in ['male homosexual', 'male heterosexual', 'male bisexual', 
                              'female homosexual', 'female heterosexual', 'female bisexual'] and not klasse_error:
                klasse_error = True
                print(f"Klasse {klasse} not one of the expected values: ['male homosexual', 'male heterosexual', 'male bisexual', 'female homosexual', 'female heterosexual', 'female bisexual']")

    print()
    print('Test 2:')
    print(f'female homo:  {round(f_ho/100, 4)}   --   {0.50*0.021}')
    print(f'male homo:    {round(m_ho/100, 4)}   --   {0.50*0.049}')
    print(f'female hetero:{round(f_he/100, 4)}   --   {0.50*0.907}')
    print(f'male hetero:  {round(m_he/100, 4)}   --   {0.50*0.900}')
    print(f'female bi:    {round(f_bi/100, 4)}   --   {0.50*0.072}')
    print(f'male bi:      {round(m_bi/100, 4)}   --   {0.50*0.051}')
    print()
    print(f'Test 3: Network is valid: {not (gender_error or klasse_error)}')