""" Lets see..
"""
import datetime
import json

from game import *


class generation_class(list):
    """extends list,
    represents a generation (or children)
    contains a list of individuals, and some generation attributes

    Args:
        list (_type_): _description_
    """
    
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        
        self.n = -1
    
    def __add__(self, *args, **kwargs): # Overwrite to return the proper class
        return generation_class(super().__add__(*args, **kwargs))
    
    def serialize(self,key:str) -> str:
        return [entry[key] for entry in self]
    
    def from_list(self,inlist:list):
        self.clear()
        for entry in inlist:
            self.append(entry)
        return self
    
    def make_filecontent(self,settings_line=""):
        writeline = "#NEWGEN "+str(self.n)+"\n"
        if settings_line != "":
            writeline += settings_line + "\n"
        for individual in self:
            individual_line = individual.make_filecontent()
            # print(individual_line)
            writeline += individual_line+"\n"
        return writeline
        
    

class individual_class(dict):
    """extends dict,
    represents an individual
    contains chromosome and then some

    Args:
        dict (_type_): _description_
    """
    def __init__(self, *args, **kwargs):
        dict.__init__(self,*args, **kwargs)
        
        
    def set_chromosome(self,chromosome):
        self['chromosome'] = chromosome
        self['ai'].weights = chromosome
        
    def make_filecontent(self):
        return json.dumps({key: self._process_val(key,val) for key,val in self.items()})
    def _process_val(self,key,val):
        if key == 'ai':
            return None
        elif key == 'chromosome':
            return val.tolist()
        
        else:
            return val
        
    def from_line(self,line):
        for key,val in json.loads(line).items():
            if val is not None:
                if key == "chromosome":
                    self.set_chromosome(np.array(val))
                else:
                    self[key] = val
        return self

class GA_settings(dict):
    """extends dict,
    contains settings

    Args:
        dict (_type_): _description_
    """
    def __init__(self, *args, **kwargs):
        dict.__init__(self,*args, **kwargs)
        
        self.set_defaults()
    
    def set_defaults(self):
        self['n_individuals'] = self.get('n_individuals',3)
        self['n_children'] = self.get('n_children',3)
        
    def make_filecontent(self):
        return "#SETTINGS "+json.dumps(self)
        return json.dumps({key: self._process_val(key,val) for key,val in self.items()})# if process needed
    def _process_val(self,key,val):
        if False:
            return None
        else:
            return val
        
    def from_file(self,instr: str):
        self.__init__(json.loads(instr.replace("#SETTINGS","")))
        return self
        
class myGA():
    def __init__(self,settings:GA_settings=GA_settings()):
        
        self.settings = settings
        self.set_default_settings()
        
    def set_default_settings(self):
        
        # Filez
        self.settings['fname'] = self.settings.get('fname',None)
        
        # Generationz
        self.settings['n_individuals'] = self.settings.get('n_individuals',3)
        self.settings['n_children'] = self.settings.get('n_children',3)
        
        # Evaluation
        self.settings['n_attempts'] = self.settings.get('n_attempts',3)
        
        # Rates
        self.settings['mutate_rate'] = self.settings.get('mutate_rate',0.5)
        self.settings['nudge_rate'] = self.settings.get('nudge_rate',0.)
        self.settings['nudge_size'] = self.settings.get('nudge_size',0.01) # std of normal distr
    
    def set_settings(self,settings:GA_settings):
        for key,val in settings.items():
            self.settings[key] = val
        
        
    def new_individual(self,ai_instance):
        
        out = individual_class({'chromosome':ai_instance.weights,'ai':ai_instance,'score':-1})
        
        out['ai'].scales[1][0] = SCREEN_HEIGHT
        out['ai'].scales[1][1] = SCREEN_WIDTH
        out['ai'].scales[1][2] = SCREEN_HEIGHT
    
        return out
    
    def eval_individual(self,individual): # I dont think this works anymore
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
    
    def eval_multiple(self,generation: generation_class,testing=False,enable_camera=True):
        if testing:
            for i,individual in enumerate(generation):
                generation[i]['score'] += np.random.randint(100,200)
            return generation
                
        # return np.random.randint(100,152)
        n_attempts = self.settings['n_attempts']
        
        thegame = MyGame(enable_camera = enable_camera)
        thegame.ai = generation.serialize('ai')
        thegame.multiple_ai = True
        
        # Reset scores
        for i,individual in enumerate(generation):
                generation[i]['score'] = 0
        
        for i in range(n_attempts): # n attempts for each AI.
            thegame.setup()
        
            arcade.run()
            # arcarde.exit() inside class, then:
            for i,score in enumerate(thegame.score_list):
                generation[i]['score'] += score
        arcade.close_window()
        return generation
    
    
    def select_parents(self,generation: generation_class,n_parents: int=2):
        
        # out = np.argsort(scores)[-len(scores)//n_parents:][::-1] # simply the best n
        scores = generation.serialize('score')
        # probability based on score
        inds = []
        powers = np.power(scores,2,dtype='f8')
        powers = powers/sum(powers)
        cumul = np.cumsum(powers)
        
        while len(inds) < n_parents:
            rando = cumul[-1]*np.random.uniform()
            ind = np.argwhere(rando <= cumul)[0][0]
            # print(scores,cumul,rando,ind,np.argwhere(rando <= cumul)[0][0])
            if ind not in inds:
                inds.append(ind)
                
        
        
        
        return inds
    
    def new_chromosome_crossover(self,generation:generation_class):
        parents = self.select_parents(generation,n_parents=2)
            
        individual1,individual2 = generation[parents[0]],generation[parents[1]]
        new1,new2 = self.crossover(individual1['chromosome'],individual2['chromosome'])
        
        
        return new1,new2
    
    def combine_parents(self,generation:generation_class,parents):# 
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
        mutate_rate = self.settings['mutate_rate']
        nudge_rate = self.settings['nudge_rate']
        nudge_size = self.settings['nudge_size']
        
        if np.random.uniform() < mutate_rate:
            ind = np.random.randint(len(chromosome))
            chromosome[ind] = np.random.uniform(-1.,1.)
        if np.random.uniform() < nudge_rate:
            ind = np.random.randint(len(chromosome))
            chromosome[ind] += np.random.normal(scale=nudge_size)
            chromosome[ind] = max(-1.,min(1.,chromosome[ind]))
        return chromosome
        
    def crossover(self,chromosome1,chromosome2):
        if False:
            # Crossover the binary reps # Doesnt work
            print(chromosome1)
            print(chromosome2)
            print(chromosome1.tobytes())
            b1 = list(chromosome1.tobytes())
            b2 = list(chromosome2.tobytes())
            breaks = np.sort(np.random.randint(0,len(b1)+1,2))
            
            b1[breaks[0]:],b2[breaks[0]:] = b2[breaks[0]:],b1[breaks[0]:]
            b1[:breaks[1]],b2[:breaks[1]] = b2[:breaks[1]],b1[:breaks[1]]
            
            print(b1,b2)
            chromosome1 = np.frombuffer(np.buffer(b1))
            chromosome2 = np.frombuffer(buffer(b2))
            print(chromosome1)
            print(chromosome2)
            
            input()
            
        
        
        # Crossover 2 lissts
        breaks = np.sort(np.random.randint(0,len(chromosome1)+1,2))
        
        out1 = chromosome1.copy()
        out2 = chromosome2.copy()
        out1[breaks[0]:breaks[1]] = chromosome2[breaks[0]:breaks[1]]
        
        out2[breaks[0]:breaks[1]] = chromosome1[breaks[0]:breaks[1]]
        
        return out1,out2
        
    def replace_generation(self,generation: generation_class,children: generation_class):
        n_individuals = len(generation)
        # Just choose best
        combined = generation + children
        combined_scores = combined.serialize('score')
        selected = np.argsort(combined_scores)[-n_individuals:][::-1] # simply the best n
        
        new_generation = generation.from_list([ combined[ind] for ind in selected ])
        
        return new_generation
        
    def output_generation(self,fname: str,generation:generation_class):
        
        settings_line = self.settings.make_filecontent()
        writeline = generation.make_filecontent(settings_line)
        
        
        with open(fname, 'a') as thefile:
            thefile.write(writeline)
            
        
        if False: # Old code
            scores = generation.serialize('score')
            for i in range(len(generation)):
                writeline = "%i\t"%generation.n
                writeline += np.array2string(generation[i]["chromosome"])
                writeline += "\t%i\n"%scores[i]
                thefile.write(writeline)
                
            
    def read_file_rawlines(self,fname: str) -> list:
        """return all lines of the file, grouped per generation

        Args:
            fname (str): _description_

        Returns:
            : _description_
        """
        out = []
        with open(fname,'r') as thefile:
            for line in thefile:
                if len(line) > 7:
                    if line[:7] == "#NEWGEN":
                        out.append([])
                        
                out[-1].append(line.strip())
        
        return out
        
    def get_last_generation_from_file(self,fname:str) -> tuple[generation_class, GA_settings]:
        all_lines = self.read_file_rawlines(fname)
        
        generation,settings = self.make_generation_from_lineblock(all_lines[-1])
        
        
        return generation,settings
    
    def make_generation_from_lineblock(self,lines:list) -> generation_class:
        
        
        generation = generation_class()
        settings = GA_settings()
        
        generation.n = int(lines[0].split()[-1])
        
        print(lines)
        if lines[1][:9] == "#SETTINGS":
            settings = settings.from_file(lines[1])
            i = 2
        else:
            i = 1
        
        generation.from_list([self.new_individual(perceptron()).from_line(line) for line in lines[i:]])
        
        return generation,settings


def main():
    # Some settings
    new_file = True
    fname = "GA_out.dat"
    
    
    # Setup GA
    theGA = myGA()
    
    # Make generation
    # Read file
    if new_file:
        open(fname, 'w').close()
        
        
        n_individuals = 8
        
        settings = GA_settings({ 'fname': fname,
                                
                                 'n_individuals': n_individuals,
                                 'n_children': 8,
                                 
                                }) 
        theGA.set_settings(settings)
        generation = generation_class().from_list([ theGA.new_individual(perceptron()) for i in range(n_individuals) ])
    else:
        generation,settings = theGA.get_last_generation_from_file(fname)
        theGA.set_settings(settings)
        
        
    # Some settings
    
    WATCH_GAMES = True
    
    # testing?
    testing = False # Makes scores random
    
    
    n_gen = 5
    # for gen in range(n_gen):
    while True:
        generation.n += 1
        
        print("> Start gen",generation.n)
        print("  ",datetime.datetime.now())
        # Fix the settings
        n_individuals = theGA.settings['n_individuals']
        n_children = theGA.settings['n_children']
        
        
        
        # Test the generation
        print("  - Eval generation")
        generation = theGA.eval_multiple(generation,testing=testing,enable_camera=WATCH_GAMES)
        # for individual in generation:
        #     score = theGA.eval_individual(individual)
        #     result['scores'].append(score)
            # print("DIED",thegame.score)
        # print(generation)
            
        print("    !Done playing")
        scores = generation.serialize('score')
        print("    scores",scores,np.mean(scores))
        
        # Produce Children
        print("  - Breed Children")
        cnt = 0
        children = generation_class()
        while cnt < n_individuals:
            childs_chromosomes = theGA.new_chromosome_crossover(generation)
            
            for child_chromosome in childs_chromosomes: # is a 2-tuple
                if cnt < n_children:
                    child_chromosome = theGA.nudge_and_mutate_chromosome(child_chromosome)
                    children.append(theGA.new_individual(perceptron()))
                    children[-1].set_chromosome(child_chromosome)
                    cnt += 1
            
        # Test Children
        print("  - Eval Children")
        children = theGA.eval_multiple(children,testing=testing,enable_camera=WATCH_GAMES)
        # for i,child in enumerate(children):
        #     score = theGA.eval_individual(child)
        #     children_scores.append(score)
        print("    scores",children.serialize('score'))
        
        # New generation
        generation = theGA.replace_generation(generation,children)
        
        
        # Write to file
        theGA.output_generation(fname,generation)
        
        # input()
        

if __name__ == "__main__":
    main()
