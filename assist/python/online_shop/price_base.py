import os
import sys
from abc import ABC, abstractmethod


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from base.formula_calculator import *


class PriceCalculatorBase(ABC):
   
    def __init__(self):
        self._calculator=FormulaCalculator()

    def set_symbols(self,symbol_dic:dict):
        self._calculator.set_symbols(symbol_dic)

    def add_variable(self,variable_name,value:str|int|float):
        self._calculator.add_variable(variable_name,value)
        
    def set_formulas(self,formulas:list[str]):
        self._calculator.set_formulas(formulas)
        
    def add_formlua(self, formula:str|list[str]):
        self._calculator.add_formlua(formula)
    
    def _calculate_impl(self,key:str,val:float,formulas:list[str]):
        self._calculator.add_variable(key,val)
        self._calculator.add_formlua(formulas)
        self._calculator.calculate()
        return self.result_info
    @property
    def result_info(self):
        return self._calculator.info()
    
    #利润作为已知条件
    @abstractmethod
    def calculate_by_profit(self,profit:float=5):
        pass


    #定价作为已知条件
    @abstractmethod
    def calculate_by_normal_price(self,normal_price:float):
        pass

    def result_value(self,key,default_value=0):
        val=self.result(key,default_value)
        return float(val)
        
    def result(self,key,default_value=0):
        return self._calculator.result(key,default_value)
    
    def formula(self,key,default_value=""):
        return self._calculator.formula(key,default_value)
    def show_formulas(self):
        self._calculator.show_formulas()
        
    def show_results(self):
        self._calculator.show_results()
    


