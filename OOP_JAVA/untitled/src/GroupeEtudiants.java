public class GroupeEtudiants {
    private etudiant[] etudiants;
    private int nb_students;

    public GroupeEtudiants() {
        this.etudiants = new etudiant[100];
        this.nb_students = 0;
    }
    public etudiant search_student(int code){
        for (int i = 0; i < this.nb_students; i++) {
            if (etudiants[i].code == code){
                return etudiants[i];
            }
        }
        return null;
    }
    public void add_student(etudiant student){
        etudiants[this.nb_students] = student;
        this.nb_students++;
    }
    public void set_name_student()

}
