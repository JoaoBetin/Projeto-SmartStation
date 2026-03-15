package SmartStation.dashboard_api.Funcionario;

import SmartStation.dashboard_api.Sessao.SessaoModel;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@NoArgsConstructor
@AllArgsConstructor
@Data
public class FuncionarioDTO {

    private Long id;

    private String nome;

    private Long matricula;

    private Cargo cargo;

    private Boolean ativo;

    private List<SessaoModel> sessaoModels;
}
