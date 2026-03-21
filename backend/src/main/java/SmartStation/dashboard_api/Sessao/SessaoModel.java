package SmartStation.dashboard_api.Sessao;

import SmartStation.dashboard_api.Funcionario.FuncionarioDTO;
import SmartStation.dashboard_api.Funcionario.FuncionarioModel;
import com.fasterxml.jackson.annotation.JsonIgnore;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.ToString;

import java.time.LocalDate;
import java.time.LocalTime;

@Data
@Entity
@Table(name = "sessao")
@NoArgsConstructor
@AllArgsConstructor
@ToString
public class SessaoModel {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private Boolean ativa;

    private LocalDate data;

    private LocalTime hora_inicio;

    private LocalTime hora_fim;

    private LocalTime tempo_ocioso;

    private Integer total_caixas;

    @ManyToOne
    @JoinColumn(name = "funcionario_id")
    @JsonIgnore
    private FuncionarioDTO funcionarioDTO;

}
