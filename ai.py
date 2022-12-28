"""lets start with simple perceptron
"""
import numpy as np
# from game import *
    
    
class perceptron():
    def __init__(self, n=6,weights=None):
        
        self.n = n
        
        if weights is None:
            self.weights = 2 * np.random.random_sample(n) -1
        else:
            self.weights = weights
    
        self.input_arr = np.ones(n) 
        self.scales = (np.zeros(n-1),np.ones(n-1))
        
        
    def activation_func(self,val):
        
        return 2*(val >= 0) - 1
    
    def run_net(self,input_vals):
        # print(input_vals)
        # print(self.scales)
        
        self.input_arr[1:] = (input_vals-self.scales[0])/self.scales[1]
        # print(self.input_arr)
        
        out = np.sum(self.input_arr*self.weights)
        out = self.activation_func(out)
        # print(out)
        # input()
        return out
    
    
def main():
    
    
    weights = 2 * np.random.random_sample(4) -1
    print(weights)
    pcp = perceptron(weights)
    
    
    tst_in = np.array([0,0.5,0.5])
    tst = pcp.run_net(tst_in)
    print(tst)
    
    input()
    
    # thegame = myGame()
    # thegame.setup()
    # thegame.run()
    
    
if __name__ == "__main__":
    main()