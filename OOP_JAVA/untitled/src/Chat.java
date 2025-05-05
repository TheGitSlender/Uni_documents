public class Chat extends Animal implements AnimalCompagnie{
    String name;

    public Chat(String name){
        super(4);
        this.name = name;

    }

    public Chat(){
        this("");
    }

    @Override
    public String getName(){
        return name;
    }

    @Override
    public void setName(String name){
        this.name = name;
    }

    @Override
    public void jouer(){
        System.out.println("Le chat joue.");
    }

    @Override
    public void manger(){
        System.out.println("Le chat " + name + "  mange.");
    }
}
