public class Poisson extends Animal implements AnimalCompagnie{
    String name;
    public Poisson(){
        super(0);
    }

    @Override
    public String getName(){
        return "";
    }

    @Override
    public void setName(String nom){
        name = nom;
    }

    @Override
    public void jouer(){}

    @Override
    public void marcher(){
        System.out.println("Le poisson ne peut pas marcher, il n'a pas de pattes");
    }

    @Override
    public void manger(){
        System.out.println("Le poisson mange des algues.");
    }


}
