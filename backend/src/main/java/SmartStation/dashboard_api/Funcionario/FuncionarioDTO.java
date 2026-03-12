package SmartStation.dashboard_api.Funcionario;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@NoArgsConstructor
@AllArgsConstructor
@Data
public class FuncionarioDTO {

    private Long id;

    private String nome;

    private Long matricula;

    private Cargo cargo;

    private boolean ativo;

}
