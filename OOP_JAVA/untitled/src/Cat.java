public class Cat extends Animal implements AnimalCompagnie {
    String name;

    Cat(String name){
        super(4);
        this.name = name;
    }

    Cat(){
        this("");
    }

    @Override
    public String get_name(){
        return this.name;
    }

    @Override
    public void set_name(String name){
        this.name = name;
    }
}
