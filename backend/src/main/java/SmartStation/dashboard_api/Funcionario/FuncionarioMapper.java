package SmartStation.dashboard_api.Funcionario;

import SmartStation.dashboard_api.Sessao.SessaoMapper;
import org.springframework.stereotype.Component;

import java.util.stream.Collectors;

@Component
public class FuncionarioMapper {

    private final SessaoMapper sessaoMapper;

    public FuncionarioMapper(SessaoMapper sessaoMapper) {
        this.sessaoMapper = sessaoMapper;
    }

    public FuncionarioDTO toDTO(FuncionarioModel funcionario) {
        if (funcionario == null) return null;

        FuncionarioDTO dto = new FuncionarioDTO();
        dto.setId(funcionario.getId());
        dto.setNome(funcionario.getNome());
        dto.setMatricula(funcionario.getMatricula());
        dto.setAtivo(funcionario.getAtivo());
        dto.setCargo(funcionario.getCargo());

        if (funcionario.getSessaoModels() != null) {
            dto.setSessaoModels(
                    funcionario.getSessaoModels().stream()
                            .map(sessaoMapper::toDTO)
                            .collect(Collectors.toList())
            );
        }

        return dto;
    }

    public FuncionarioModel toEntity(FuncionarioDTO dto) {
        if (dto == null) return null;

        FuncionarioModel funcionario = new FuncionarioModel();
        funcionario.setId(dto.getId());
        funcionario.setNome(dto.getNome());
        funcionario.setMatricula(dto.getMatricula());
        funcionario.setAtivo(dto.getAtivo());
        funcionario.setCargo(dto.getCargo());

        return funcionario;
    }
}
