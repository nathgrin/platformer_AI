""" Lets see..
"""

from game import *
from misc_func import *

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
        
    

def make_genome(chromosome: np.array) -> str:
    """make a genome from a chromosome
    convert each value in the chromosome to a letter 1-26 A-Z
    
    Args:
        chromosome (np.array): list of floats

    Returns:
        str: literally string of letters, one for each val in chromosome
    """
    themin = -1.
    themax = 1.
    
    genome = ""
    for val in chromosome:
        scaled = 26*(val-themin)/(themax-themin)
        for i,let in enumerate(string.ascii_uppercase):
            
            if scaled <= i+1:
                genome += let
                break
    
    return genome


class id_manager():
    """
    chomo_id: g<generation n>.G<genome>.P<parents g,genome, joint by ; if multiple>.T<babytype Random, Mutated,CrossOver>.M<mutation indices>
    As of now: IDs are not guaranteed to be unique!
    
    Returns:
        _type_: _description_
    """
    label_order = "gGPTM"
    
    def __init__(self):
        pass
    def new_id(self,Gn:int=-1,genome:str="",parents:list=[],babytype:str="",mutation:str="")->str:
        if type(parents) == list:
            parents = self.join_parentvals(parents)
        parents = parents.replace('.',',')
        out_id = "g:%i.G:%s.P:%s.T:%s.M:%s"%(Gn,genome,parents,babytype,mutation)
        
        return out_id
    
    def get_index_from_label(self,label:str)->int:
        return self.label_order.index(label)
    
    def id_replace_value(self,the_id:str,ind:str,val:str)->str:
        
        if type(ind) == str:
            ind = self.get_index_from_label(ind)
        
        splitted = the_id.split('.')
        second_split = splitted[ind].split(':')
        second_split[1] = val.replace('.',',').replace(":",";") # Skip the first letter
        splitted[ind] = ":".join(second_split)
        
        return ".".join(splitted)
    
    def id_get_value(self,the_id:str,ind:str)->str:
        
        if type(ind) == str:
            ind = self.get_index_from_label(ind)
        splitted = the_id.split('.')
        return splitted[ind].split(":")[1]
    
    def make_parentval(self,the_id):
        splitted = the_id.split('.')
        return ",".join( [x[2:] for x in splitted[:2]]) # skip the labels
    
    def join_parentvals(self,vals:list) -> str:
        return ";".join(vals)
idclass= id_manager()

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
        
        self['genome'] = make_genome(chromosome)
        self['id'] = idclass.id_replace_value(self['id'],'G',self['genome'])
        
    
        
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
        
        self['n_inputs'] = self.get('n_inputs',4)
        
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
        
        self.settings = GA_settings()
        self.set_default_settings()
        self.set_settings(settings)
        
    def set_default_settings(self):
        
        # Filez
        self.settings['loc'] = self.settings.get('loc',"")
        self.settings['fname'] = self.settings.get('fname',None)
        
        
        # Individuals
        self.settings['n_inputs'] = self.settings.get('n_inputs',4)
        
        # Generationz
        self.settings['n_individuals'] = self.settings.get('n_individuals',3)
        self.settings['n_children'] = self.settings.get('n_children',3)
        
        # Evaluation
        self.settings['n_attempts'] = self.settings.get('n_attempts',3)
        
        # Rates
        self.settings['mutate_rate'] = self.settings.get('mutate_rate',0.5)
        self.settings['nudge_rate'] = self.settings.get('nudge_rate',0.)
        self.settings['nudge_size'] = self.settings.get('nudge_size',0.01) # std of normal distr
        
        # Make baby settings
        self.settings['makebaby_fullrandom_proportion'] = self.settings.get('makebaby_fullrandom_proportion',1)
        self.settings['makebaby_mutatebaby_proportion'] = self.settings.get('makebaby_mutatebaby_proportion',2)
        self.settings['makebaby_crossover_proportion']  = self.settings.get('makebaby_crossover_proportion',4)
        
    
    def set_settings(self,settings:GA_settings):
        for key,val in settings.items():
            print(key,val)
            if key not in self.settings.keys():
                print("WARNING: Did not recognize key: %s. Did you mean one of:"%(key),self.settings.keys(),"?")
            self.settings[key] = val
        
        
    def new_individual(self,ai_instance):
        
        out = individual_class({'chromosome':ai_instance.weights,'ai':ai_instance,'score':-1,'id':idclass.new_id()})
        
        out['ai'].scales[1][0] = PLAYER_MAX_FUEL
        out['ai'].scales[1][1] = SCREEN_HEIGHT
        out['ai'].scales[1][2] = SCREEN_WIDTH
        out['ai'].scales[1][3] = SCREEN_HEIGHT
        out['ai'].scales[1][4] = SCREEN_WIDTH
        out['ai'].scales[1][5] = SCREEN_HEIGHT
    
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
                generation[i]['score'] = np.random.randint(100,200)
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
    
    def new_chromosome_crossover(self,generation:generation_class,parent_inds:list):
            
        individual1,individual2 = generation[parent_inds[0]],generation[parent_inds[1]]
        new1,new2 = self.crossover(individual1['chromosome'],individual2['chromosome'])
        
        
        return new1,new2
    
    def combine_parents(self,generation:generation_class,parents):# 
        out = []
        # print("NEW GEN")
        # print(out)
        
        cnt = 0
        
        n_children = self.settings['children']
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
        id_strs = ["" for x in out]
        # Nudge and mutate
        for i in range(len(out)):
            out[i],id_strs[i] = self.nudge_and_mutate_chromosome(out[i])
            
            
        # print(generation)
        # print(out)
        
        # input()
        return out,id_strs
    
    
    def nudge_and_mutate_chromosome(self,chromosome):
        mutate_rate = self.settings['mutate_rate']
        nudge_rate = self.settings['nudge_rate']
        nudge_size = self.settings['nudge_size']
        
        id_str = ""
        if np.random.uniform() < mutate_rate:
            ind = np.random.randint(len(chromosome))
            chromosome[ind] = np.random.uniform(-1.,1.)
            id_str += "%02i"%(ind)
        if np.random.uniform() < nudge_rate:
            ind = np.random.randint(len(chromosome))
            chromosome[ind] += np.random.normal(scale=nudge_size)
            chromosome[ind] = max(-1.,min(1.,chromosome[ind]))
            id_str += "%02i"%(ind)
        return chromosome,id_str
    
    def make_baby(self,generation: generation_class)->list:
        
            
        idclass = id_manager()
        
        # yes we'll get these from settings at some point
        makebaby_fullrandom_proportion = self.settings['makebaby_fullrandom_proportion']
        makebaby_mutatebaby_proportion = self.settings['makebaby_mutatebaby_proportion']
        makebaby_crossover_proportion  = self.settings['makebaby_crossover_proportion']
        
        tot = makebaby_fullrandom_proportion + makebaby_mutatebaby_proportion + makebaby_crossover_proportion
        
        rando = np.random.uniform(tot)
        
        if rando < makebaby_fullrandom_proportion: # Random baby
            childs_chromosomes = ( np.random.uniform(-1.,1.,len(generation[0]['chromosome'])), )
            chromo_id = idclass.new_id(Gn=generation.n , babytype="R")
            # print(childs_chromosomes)
        elif rando < makebaby_mutatebaby_proportion: # Mutated baby
            parent_inds = self.select_parents(generation,n_parents=1)
            childs_chromosomes = generation[parent_inds[0]]['chromosome'].copy()
            # random number of random mutations
            chromo_id = idclass.new_id(Gn=generation.n , parents=idclass.make_parentval(generation[parent_inds[0]]['id']), babytype="M")
            chromo_id_mutation = ""
            for ind in np.random.permutation(len(childs_chromosomes))[:np.random.randint(1,len(childs_chromosomes)-1)]:
                chromo_id_mutation += "%02i"%(ind)
                childs_chromosomes[ind] = np.random.uniform(-1.,1.)
            chromo_id = idclass.id_replace_value(chromo_id,"M",chromo_id_mutation)
            childs_chromosomes = (childs_chromosomes,)
            
            
        else : # Crossover baby
            parent_inds = self.select_parents(generation,n_parents=2)
            childs_chromosomes= self.new_chromosome_crossover(generation,parent_inds)
            
            parent_ids = [idclass.make_parentval(generation[parent_inds[0]]['id']),idclass.make_parentval(generation[parent_inds[1]]['id'])]
            chromo_id = idclass.new_id(Gn=generation.n, parents = parent_ids, babytype="CO")
        
        return childs_chromosomes,chromo_id
        
        
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
        
        
        print(2*"    "+"selected:"," ".join([ "%i+%i"%(n_individuals* (i//n_individuals),i%n_individuals) for i in selected]))
        
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
        
    def read_file(self,fname: str):
        
        all_lines = self.read_file_rawlines(fname)
        
        out = [ self.make_generation_from_lineblock(lines) for lines in all_lines ]
        
        return out
        
        
    def get_last_generation_from_file(self,fname:str) -> tuple[generation_class, GA_settings]:
        all_lines = self.read_file_rawlines(fname)
        
        generation,settings = self.make_generation_from_lineblock(all_lines[-1])
        
        
        return generation,settings
    
    def make_generation_from_lineblock(self,lines:list) -> generation_class:
        """process input from a file. a block of lines which are the generation

        Args:
            lines (list): _description_

        Returns:
            generation_class: _description_
        """
        
        
        generation = generation_class()
        settings = GA_settings()
        
        generation.n = int(lines[0].split()[-1])
        
        
        if lines[1][:9] == "#SETTINGS":
            settings = settings.from_file(lines[1])
            i = 2
        else:
            i = 1
        
        n_inputs = settings.get("n_inputs")
        generation.from_list([self.new_individual(perceptron(n=settings['n_inputs']+1)).from_line(line) for line in lines[i:]])
        
        return generation,settings


def main():
    # Some settings
    new_file = True
    loc = "data/"
    fname = "GA_out.dat"
    
    print(make_genome([0.96804840333239, -0.7832400110631503, -0.35330159640945613, -0.9326598832855191, 0.530784518290786]))
    
    # Setup GA
    theGA = myGA()
    
    # Make generation
    # Read file
    if new_file:
        open(loc+fname, 'w').close()
        
        
        n_individuals = 24
        
        settings = GA_settings({ 'loc': loc,
                                 'fname': fname,
                                
                                 'n_individuals': n_individuals,
                                 'n_children': n_individuals,
                                 
                                 'n_inputs': 6,
                                 
                                 'n_attempts': 5,
                                 
                                 'makebaby_fullrandom_proportion': 1,
                                 'makebaby_mutatebaby_proportion': 2,
                                 'makebaby_crossover_proportion': 5,
                                 
                                 'tst': 10
                                 
                                }) 
        theGA.set_settings(settings)
        generation = generation_class().from_list([ theGA.new_individual(perceptron(n=settings['n_inputs']+1)) for i in range(n_individuals) ])
        # Fix ids:
        for individual in generation:
            individual['id'] = idclass.id_replace_value(individual['id'],'g',"0")
            individual['id'] = idclass.id_replace_value(individual['id'],'G',make_genome(individual['chromosome']))
    else:
        generation,settings = theGA.get_last_generation_from_file(loc+fname)
        theGA.set_settings(settings)
        
        
    # Some settings
    
    WATCH_GAMES = False
    
    # testing?
    testing = False # Makes scores random
    
    last_time = datetime.datetime.now()
    
    n_gen = 5
    # for gen in range(n_gen):
    while True:
        generation.n += 1
        
        print("> Start gen",generation.n)
        now_time = datetime.datetime.now()
        print(" ",now_time,"(",now_time-last_time,")")
        last_time = now_time
        # Fix the settings
        n_individuals = theGA.settings['n_individuals']
        n_children = theGA.settings['n_children']
        
        n_inputs = theGA.settings['n_inputs'] # for ai
        
        # print(n_children)
        
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
        ids = generation.serialize('id')
        print("    scores","mean:",np.mean(scores))
        print(fmt_score_log(scores,ids))
        
        # Produce Children
        print("  - Breed Children")
        cnt = 0
        children = generation_class()
        while cnt < n_children:
            childs_chromosomes,chromo_id = theGA.make_baby(generation)
            
            for child_chromosome in childs_chromosomes: # crossover gives 2-tuple
                if cnt < n_children:
                    child_chromosome,chromo_id_mutation = theGA.nudge_and_mutate_chromosome(child_chromosome)
                    chromo_id = idclass.id_replace_value(chromo_id,"M",idclass.id_get_value(chromo_id,"M")+chromo_id_mutation)
                    children.append(theGA.new_individual(perceptron(n=n_inputs+1)))
                    children[-1]['id'] = chromo_id # first set id, set_chromosome will update the chromosome
                    children[-1].set_chromosome(child_chromosome)
                    cnt += 1
            
        # Test Children
        print("  - Eval Children")
        children = theGA.eval_multiple(children,testing=testing,enable_camera=WATCH_GAMES)
        # for i,child in enumerate(children):
        #     score = theGA.eval_individual(child)
        #     children_scores.append(score)
        scores = children.serialize('score')
        ids = children.serialize('id')
        print("    scores","mean:",np.mean(scores))
        print(fmt_score_log(scores,ids))
        
        # New generation
        generation = theGA.replace_generation(generation,children)
        
        
        
        # Write to file
        theGA.output_generation(loc+fname,generation)
        
        # input()
        

if __name__ == "__main__":
    main()
