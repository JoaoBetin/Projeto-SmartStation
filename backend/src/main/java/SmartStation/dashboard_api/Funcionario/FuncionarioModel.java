package SmartStation.dashboard_api.Funcionario;

import SmartStation.dashboard_api.Sessao.SessaoModel;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.ToString;
import org.hibernate.annotations.IdGeneratorType;

import java.util.List;


@Data
@Entity
@Table(name = "funcionario")
@NoArgsConstructor
@AllArgsConstructor
@ToString
public class FuncionarioModel {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String nome;

    private Long matricula;

    private Boolean ativo;

    private Cargo cargo;

    @OneToMany(mappedBy = "funcionarioModel")
    private List<SessaoModel> sessaoModels;
}
