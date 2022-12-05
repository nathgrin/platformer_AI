""" Lets see..
"""

from game import *

class myGA():
    def __init__(self,rates={},settings={}):
        
        self.mutate_rate = rates.get('mutate_rate',0.2)
        self.nudge_rate = rates.get('nudge_rate',0.)
        self.nudge_size = settings.get('nudge_size',0.01) # std of normal distr
        
        
    def new_individual(self,ai_instance):
        
        out = {'chromosone':ai_instance.weights,'ai':ai_instance}
        return out
    
    def select_parents(self,scores):
        """returns top-to-bottom"""
        
        # print(np.argsort(scores))
        # print(np.argsort(scores)[-len(scores)//3:][::-1])
        # input()
        return np.argsort(scores)[-len(scores)//3:][::-1]
    
    def nextgen_chromosones(self,individuals,parents):
        
        out = []
        # print("NEW GEN")
        # print(out)
        
        cnt = 0
        
        # Mating
        for i,par1 in enumerate(parents):
            indivi1 = individuals[par1]
            for j,par2 in enumerate(parents):
                if i != j:
                    indivi2 = individuals[par2]
                    
                    new1,new2 = self.crossover(indivi1['chromosone'],indivi2['chromosone'])
                    out.append(new1)
                    cnt += 1
                    if cnt < len(individuals):
                        out.append(new2)
                        cnt += 1
                if cnt >= len(individuals):
                    break
            if cnt >= len(individuals):
                break
        
        
        # print(len(out),len(individuals))
        # Fill list with ... parents
        while len(out)<len(individuals):
            for par in parents:
                
                
                out.append(individuals[par]['chromosone'])
                if len(out) == len(individuals):
                    break
                
                
        # print(individuals)
        # print(out)
        return out
        
    def nudgeandmutate_chromosones(self,chromosones):
        out = chromosones
        # Nudge and mutate
        mutate_rate = self.mutate_rate
        nudge_rate = self.nudge_rate
        nudge_size = self.nudge_size
        for i in range(len(out)):
            if np.random.uniform() < mutate_rate:
                # print("MUTATE",out[i])
                ind = np.random.randint(len(out[i]))
                out[i][ind] = np.random.uniform(-1.,1.)
                # print(out[i])
            if np.random.uniform() < nudge_rate:
                # print("NUDGE",out[i])
                ind = np.random.randint(len(out[i]))
                out[i][ind] += np.random.normal(scale=nudge_size)
                out[i][ind] = max(-1.,min(1.,out[i][ind]))
                # print(out[i])
            
            
        # print(individuals)
        # print(out)
        
        # input()
        return out
        
    def crossover(self,chromosone1,chromosone2):
        breaks = np.sort(np.random.randint(0,len(chromosone1)+1,2))
        
        out1 = chromosone1.copy()
        out2 = chromosone2.copy()
        out1[breaks[0]:breaks[1]] = chromosone2[breaks[0]:breaks[1]]
        
        out2[breaks[0]:breaks[1]] = chromosone1[breaks[0]:breaks[1]]
        
        return out1,out2
        
    def replace_individuals(self,individuals,chromosones):
        
        
        for i,chromosone in enumerate(chromosones):
            individuals[i]['chromosone'] = chromosone
            individuals[i]['ai'].weights = chromosone
            
        return individuals
        
    def output_gen(self,fname,gen,individuals,scores):
        with open(fname, 'a') as thefile:
            for i in range(len(individuals)):
                writeline = "%i\t"%gen
                writeline += np.array2string(individuals[i]["chromosone"])
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
        
        
        

def main():
    new_file = False
    fname = "GA_out.dat"
    
    # Setup GA
    theGA = myGA()
    
    # Make individuals
    individuals = [ theGA.new_individual(perceptron()) for i in range(8) ]
    
    
    for indivi in individuals:
        indivi['ai'].scales[1][0] = SCREEN_HEIGHT
        indivi['ai'].scales[1][1] = SCREEN_WIDTH
        indivi['ai'].scales[1][2] = SCREEN_HEIGHT
            
    if new_file:
        open(fname, 'w').close()
        gen = -1
        
    else:
        
        all_gens = theGA.read_file(fname)
        gen= len(all_gens)-1
        
        for i, data in enumerate(all_gens[-1]):
            print(data)
            individuals[i]['chromosone'] = data[1]
            individuals[i]['ai'].weights = data[1]
            
        
        
        
        
    
    WATCH_GAMES = False
    # Make game
    # thegame = MyGame(enable_camera = WATCH_GAMES)
        
    
    n_gen = 5
    # for gen in range(n_gen):
    while True:
        gen += 1
        
        print(" > Start gen",gen)
        result = {'scores':[]}
        
        for indivi in individuals:
            thegame = MyGame(enable_camera = WATCH_GAMES)
            thegame.ai = indivi['ai']
            score = 0
            for i in range(3): # n attempts for each AI.
                thegame.setup()
            
                arcade.run()
                # arcarde.exit() inside class, then:
                score += thegame.score
            arcade.close_window()
            result['scores'].append(score)
            # print("DIED",thegame.score)
            
            
        print(" !Done playing")
        print(" scores",result['scores'])
        # Write to file
        theGA.output_gen(fname,gen,individuals,result['scores'])
        
        # New generation
        parents = theGA.select_parents(result['scores'])
        print(" parents",parents)
        chromosones = theGA.nextgen_chromosones(individuals,parents)
        chromosones = theGA.nudgeandmutate_chromosones(chromosones)
        individuals = theGA.replace_individuals(individuals,chromosones)
        

if __name__ == "__main__":
    main()
