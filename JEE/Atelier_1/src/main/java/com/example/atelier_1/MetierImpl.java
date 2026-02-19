package com.example.atelier_1;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

@Component
public class MetierImpl implements IMetier{
    @Autowired
    public IData datacall;

    @Override
    public double calcul(){
        return datacall.getData() * 2;
    }

    public void setDatacall(IData datacall){
        this.datacall = datacall;
    }
}
