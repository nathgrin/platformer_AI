""" Lets see..
"""
import datetime

from game import *

class myGA():
    def __init__(self,rates={},settings={}):
        
        self.mutate_rate = rates.get('mutate_rate',0.5)
        self.nudge_rate = rates.get('nudge_rate',0.)
        self.nudge_size = settings.get('nudge_size',0.01) # std of normal distr
        
        
    def new_individual(self,ai_instance):
        
        out = {'chromosome':ai_instance.weights,'ai':ai_instance}
        return out
    
    def eval_individual(self,individual):
        # return np.random.randint(100,152)
        n_attempts = 3
        
        thegame = MyGame(enable_camera = WATCH_GAMES)
        thegame.ai = individual['ai']
        score = 0
        for i in range(n_attempts): # n attempts for each AI.
            thegame.setup()
        
            arcade.run()
            # arcarde.exit() inside class, then:
            score += thegame.score
        arcade.close_window()
        return score
    
    def eval_multiple(self,generation,enable_camera=True):
        # return np.random.randint(100,152)
        n_attempts = 3
        
        thegame = MyGame(enable_camera = enable_camera)
        thegame.ai = [individual['ai'] for individual in generation]
        thegame.multiple_ai = True
        
        scores = [0 for i in generation]
        for i in range(n_attempts): # n attempts for each AI.
            thegame.setup()
        
            arcade.run()
            # arcarde.exit() inside class, then:
            for i,score in enumerate(thegame.score_list):
                scores[i] += score
        arcade.close_window()
        return scores
    
    def select_parents(self,scores: list,n_parents: int=2):
        
        # out = np.argsort(scores)[-len(scores)//n_parents:][::-1] # simply the best n
        
        # probability based on score
        inds = []
        cumul = np.cumsum(np.power(scores,2))
        while len(inds) < n_parents:
            rando = cumul[-1]*np.random.uniform()
            ind = np.argwhere(rando <= cumul)[0][0]
            if ind not in inds:
                inds.append(ind)
                
        
        
        
        return inds
    
    def new_chromosome_crossover(self,generation,scores):
        parents = self.select_parents(scores,n_parents=2)
            
        individual1,individual2 = generation[parents[0]],generation[parents[1]]
        new1,new2 = self.crossover(individual1['chromosome'],individual2['chromosome'])
        
        
        return new1,new2
    
    def combine_parents(self,generation,parents):# 
        out = []
        # print("NEW GEN")
        # print(out)
        
        cnt = 0
        
        n_children = 8
        # print(parents)
        
        # Mate until enough children
        while cnt < n_children:
            ind1 = np.random.randint(len(parents))
            ind2 = np.random.randint(len(parents))
            while ind1 == ind2:
                ind2 = np.random.randint(len(parents))
            
            individual1,individual2 = generation[parents[ind1]],generation[parents[ind2]]
            new1,new2 = self.crossover(individual1['chromosome'],individual2['chromosome'])
            out.append(new1)
            cnt += 1
            if cnt < n_children:
                out.append(new2)
                cnt += 1
        
        return out
        
        # Mate with all parents
        for i,par1 in enumerate(parents):
            individual1 = generation[par1]
            for j,par2 in enumerate(parents):
                if i != j:
                    individual2 = generation[par2]
                    
                    new1,new2 = self.crossover(individual1['chromosome'],individual2['chromosome'])
                    out.append(new1)
                    cnt += 1
                    if cnt < len(generation):
                        out.append(new2)
                        cnt += 1
                if cnt >= len(generation):
                    break
            if cnt >= len(generation):
                break
        
        return out
        
    def nudge_and_mutate_chromosomes(self,chromosomes):
        out = chromosomes
        # Nudge and mutate
        for i in range(len(out)):
            out[i] = self.nudge_and_mutate_chromosome(out[i])
            
            
        # print(generation)
        # print(out)
        
        # input()
        return out
    
    def nudge_and_mutate_chromosome(self,chromosome):
        mutate_rate = self.mutate_rate
        nudge_rate = self.nudge_rate
        nudge_size = self.nudge_size
        
        if np.random.uniform() < mutate_rate:
            ind = np.random.randint(len(chromosome))
            chromosome[ind] = np.random.uniform(-1.,1.)
        if np.random.uniform() < nudge_rate:
            ind = np.random.randint(len(chromosome))
            chromosome[ind] += np.random.normal(scale=nudge_size)
            chromosome[ind] = max(-1.,min(1.,chromosome[ind]))
        return chromosome
        
    def crossover(self,chromosome1,chromosome2):
        breaks = np.sort(np.random.randint(0,len(chromosome1)+1,2))
        
        out1 = chromosome1.copy()
        out2 = chromosome2.copy()
        out1[breaks[0]:breaks[1]] = chromosome2[breaks[0]:breaks[1]]
        
        out2[breaks[0]:breaks[1]] = chromosome1[breaks[0]:breaks[1]]
        
        return out1,out2
        
    def replace_generation(self,generation,scores,children,children_scores):
        n_individuals = len(generation)
        # Just choose best
        combined = generation + children
        combined_scores = scores + children_scores
        selected = np.argsort(combined_scores)[-n_individuals:][::-1] # simply the best n
        
        new_generation = [ combined[ind] for ind in selected ]
        
        
        return new_generation
        
    def output_gen(self,fname,gen,generation,scores):
        with open(fname, 'a') as thefile:
            for i in range(len(generation)):
                writeline = "%i\t"%gen
                writeline += np.array2string(generation[i]["chromosome"])
                writeline += "\t%i\n"%scores[i]
                thefile.write(writeline)
                
            
    def read_file(self,fname):
        
        out = []
        with open(fname,'r') as thefile:
            for line in thefile:
                line = line.split('\t')
                # print(line)
                # print(int(line[0]) +1 > len(out))
                if int(line[0]) +1 > len(out):
                    out.append([])
                out[-1].append([
                    int(line[0]),
                    np.fromstring(line[1].replace('[','').replace(']',''), sep=" "),
                    int(line[2]) ])
                
        # print(out)
        # input()
        return out
        
        
def individual_set_chromosome(indi,chromosome):
    
    indi['chromosome'] = chromosome
    indi['ai'].weights = chromosome
    return indi
        

def main():
    new_file = False
    fname = "GA_out.dat"
    
    # Setup GA
    theGA = myGA()
    
    # Make generation
    generation = [ theGA.new_individual(perceptron()) for i in range(8) ]
    
    
    for individual in generation:
        individual['ai'].scales[1][0] = SCREEN_HEIGHT
        individual['ai'].scales[1][1] = SCREEN_WIDTH
        individual['ai'].scales[1][2] = SCREEN_HEIGHT
    
    # Read file
    if new_file:
        open(fname, 'w').close()
        gen = -1
        
    else:
        all_gens = theGA.read_file(fname)
        gen= len(all_gens)-1
        
        for i, data in enumerate(all_gens[-1]):
            generation[i] = individual_set_chromosome(generation[i], data[1])
        
        
        
        
    # Some settings
    n_children = 8
    
    WATCH_GAMES = False
    
    # testing?
    testing = False
    
    
    n_gen = 5
    # for gen in range(n_gen):
    while True:
        gen += 1
        
        print(" > Start gen",gen)
        print(datetime.datetime.now())
        result = {'scores':[]}
        
        # Test the generation
        print("Eval generation")
        result['scores'] = theGA.eval_multiple(generation,enable_camera=WATCH_GAMES)
        # for individual in generation:
        #     score = theGA.eval_individual(individual)
        #     result['scores'].append(score)
            # print("DIED",thegame.score)
            
            
        print(" !Done playing")
        print(" scores",result['scores'],np.mean(result['scores']))
        # Write to file
        theGA.output_gen(fname,gen,generation,result['scores'])
        
        # Produce Children
        cnt = 0
        children = []
        while cnt < n_children:
            childs_chromosomes = theGA.new_chromosome_crossover(generation,result['scores'])
            
            for child_chromosome in childs_chromosomes: # is a 2-tuple
                if cnt < n_children:
                    child_chromosome = theGA.nudge_and_mutate_chromosome(child_chromosome)
                    children.append(theGA.new_individual(perceptron()))
                    individual_set_chromosome(children[-1],child_chromosome)
                    cnt += 1
            
        # Test Children
        print("Play Children")
        children_scores = []
        children_scores = theGA.eval_multiple(children,enable_camera=WATCH_GAMES)
        # for i,child in enumerate(children):
        #     score = theGA.eval_individual(child)
        #     children_scores.append(score)
        
        # New generation
        generation = theGA.replace_generation(generation,result['scores'],children,children_scores)
        

if __name__ == "__main__":
    main()
