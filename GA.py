""" Lets see..
"""

from game import *

class myGA():
    def __init__(self):
        pass
    
    def select_parents(self,parents,scores):
        
        
        print(np.argsort(scores))
        
        

def main():
    
    # Make game
    thegame = MyGame()
    
    # Setup GA
    theGA = myGA()
    # Make individuals
    individuals = [ perceptron() for i in range(8) ]
    
    for indivi in individuals:
        indivi.scales[1][0] = SCREEN_HEIGHT
        indivi.scales[1][1] = SCREEN_WIDTH
        indivi.scales[1][2] = SCREEN_HEIGHT
    
    n_gen = 1#5
    for gen in range(n_gen):
        
        result = {'scores':[]}
        
        for indivi in individuals:
            thegame.setup()
            thegame.ai = indivi
        
            arcade.run()
            # arcarde.exit() inside class, then:
            result['scores'].append(thegame.score)
            print("DIED",thegame.score)
            
            
            
        # New generation
        theGA.select_parents(individuals,result['scores'])
        
        print(result['scores'])

if __name__ == "__main__":
    main()
