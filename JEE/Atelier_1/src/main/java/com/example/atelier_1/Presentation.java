package com.example.atelier_1;

import java.io.InputStream;
import java.lang.reflect.Method;
import java.util.Scanner;

public class Presentation {
    public static void main(String[] args) throws Exception{
        InputStream is = Presentation.class.getClassLoader().getResourceAsStream("config.txt");
        Scanner sc = new Scanner(is);

        String dataClassName = sc.nextLine().trim();
        Class<?> dataClass = Class.forName(dataClassName);
        IData data = (IData) dataClass.getDeclaredConstructor().newInstance();

        String metierClassName = sc.nextLine().trim();
        Class<?> metierClass = Class.forName(metierClassName);
        IMetier metier = (IMetier) metierClass.getDeclaredConstructor().newInstance();

        Method setter = metierClass.getMethod("setDatacall", IData.class);
        setter.invoke(metier, data);

        System.out.println("Result: " + metier.calcul());
    }
}
