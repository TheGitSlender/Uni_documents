public class etudiant extends Personne{
     int code;
     String univ_name;
     double grade;

    public etudiant(String nom, int code, String univ_name, double grade){
        super(nom);
        this.code = code;
        this.univ_name = univ_name;
        this.grade = grade;
    }
    @Override
    public void sePresenter(){
        System.out.println("Je suis un étudiant à " + univ_name + " et je m'appelle " + this.getNom());
    }
    public void setCode(int code){
        this.code = code;
    }
    public void setUniversite(String new_name){
        this.univ_name = new_name;
    }
    public void setMoyenne(double new_grade){
        this.grade = new_grade;
    }
    public boolean equals(etudiant e){
        return (this.code==e.code);
    }
}


