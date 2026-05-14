package DTOs;

import Enums.Cargo;
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

    private List<SessaoDTO> sessaoModels;
}
