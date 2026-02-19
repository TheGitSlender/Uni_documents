package com.example.atelier_1;

import org.springframework.stereotype.Component;

@Component("data")
public class DataImpl implements IData {
        @Override
        public double getData(){
            return 15;
        }
}
