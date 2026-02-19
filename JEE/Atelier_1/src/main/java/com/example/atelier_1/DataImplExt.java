package com.example.atelier_1;
import org.springframework.stereotype.Component;

@Component()
public class DataImplExt implements IData {
    @Override
    public double getData(){
        return 42.0;
    }
}
