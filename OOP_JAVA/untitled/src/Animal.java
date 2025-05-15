abstract class Animal {
    protected int pattes;

    protected Animal(int pattes){
        this.pattes = pattes;
    }
    abstract void manger();
    public void marcher(){
        System.out.println("L'animal marche à "+ this.pattes + " pattes");
    }
}