package SmartStation.dashboard_api.Funcionario;

import org.springframework.stereotype.Component;

@Component
public class FuncionarioMapper {

    public FuncionarioDTO toDTO(FuncionarioModel funcionario) {
        if (funcionario == null) {
            return null;
        }

        FuncionarioDTO dto = new FuncionarioDTO();
        dto.setId(funcionario.getId());
        dto.setNome(funcionario.getNome());
        dto.setMatricula(funcionario.getMatricula());
        dto.setAtivo(funcionario.getAtivo());
        dto.setSessaoModels(funcionario.getSessaoModels());
        dto.setCargo(funcionario.getCargo());

        return dto;
    }

    public FuncionarioModel toEntity(FuncionarioDTO dto) {
        if (dto == null) {
            return null;
        }

        FuncionarioModel funcionario = new FuncionarioModel();

        funcionario.setId(dto.getId());
        funcionario.setNome(dto.getNome());
        funcionario.setMatricula(dto.getMatricula());
        funcionario.setAtivo(dto.getAtivo());
        funcionario.setSessaoModels(dto.getSessaoModels());
        funcionario.setCargo(dto.getCargo());

        return funcionario;
    }
}
