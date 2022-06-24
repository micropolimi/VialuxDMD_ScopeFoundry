# -*- coding: utf-8 -*-
"""
Created on Thu Jun 24 18:12:05 2021
@authors: Elena Corbetta, Andrea Bassi. Politecnico di Milano

"""

from ScopeFoundry import BaseMicroscopeApp

class vialux_dmd_app(BaseMicroscopeApp):
    

    name = 'vialux_dmd_app'
    
    def setup(self):
        
        #Add hardware components
        print("Adding Hardware Components")
        from DMD_hw import VialuxDmdHW
        self.add_hardware(VialuxDmdHW(self))
           

        self.ui.show()
        self.ui.activateWindow()


if __name__ == '__main__':
    import sys
    
    app = vialux_dmd_app(sys.argv)
    sys.exit(app.exec_())