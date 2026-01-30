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

    #################
    f_ho, m_ho = 0.0, 0.0
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
    print('Test 2: proportion of classes in network vs proportions used in the parameters')
    print(f'female homo:  {round(f_ho/100, 4)}   --   {0.50*0.021}')
    print(f'male homo:    {round(m_ho/100, 4)}   --   {0.50*0.049}')
    print(f'female hetero:{round(f_he/100, 4)}   --   {0.50*0.907}')
    print(f'male hetero:  {round(m_he/100, 4)}   --   {0.50*0.900}')
    print(f'female bi:    {round(f_bi/100, 4)}   --   {0.50*0.072}')
    print(f'male bi:      {round(m_bi/100, 4)}   --   {0.50*0.051}')
    print()
    print(f'Test 3: Network is valid: {not (gender_error or klasse_error)}')