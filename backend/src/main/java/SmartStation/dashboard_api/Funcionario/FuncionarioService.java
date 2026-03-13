package SmartStation.dashboard_api.Funcionario;

import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

@Service
public class FuncionarioService {
    private final FuncionarioMapper funcionarioMapper;
    private final FuncionarioRepository funcionarioRepository;

    public FuncionarioService(FuncionarioMapper funcionarioMapper, FuncionarioRepository funcionarioRepository) {
        this.funcionarioMapper = funcionarioMapper;
        this.funcionarioRepository = funcionarioRepository;
    }

    // Listar Todos
    public List<FuncionarioDTO> listarFuncionarios(){
        List<FuncionarioModel> funcionarioModelList = funcionarioRepository.findAll();

        return funcionarioModelList.stream()
                .map(funcionarioMapper::toDTO)
                .collect(Collectors.toList());
    }

    // Listar por ID
    public FuncionarioDTO listarFuncionariosID(Long id){
        Optional<FuncionarioModel> funcionarioModel = funcionarioRepository.findById(id);

        return funcionarioModel.map(funcionarioMapper::toDTO).orElse(null);
    }

    // Deletar
    public void deletarFuncionario(Long id){
        funcionarioRepository.deleteById(id);
    }

    // Alterar ID
    public FuncionarioDTO alterarFuncionario(Long id, FuncionarioDTO funcionarioDTO){
        FuncionarioModel funcionarioModel = funcionarioRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Funcionario nao encontrado"));

        if(funcionarioDTO.getAtivo() != null){
            funcionarioModel.setAtivo(funcionarioDTO.getAtivo());
        }

        if(funcionarioDTO.getMatricula() != null){
            funcionarioModel.setMatricula(funcionarioDTO.getMatricula());
        }

        if(funcionarioDTO.getNome() != null){
            funcionarioModel.setNome(funcionarioDTO.getNome());
        }

        if(funcionarioDTO.getCargo() != null){
            funcionarioModel.setCargo(funcionarioDTO.getCargo());
        }

        FuncionarioModel funcionarioSalvo = funcionarioRepository.save(funcionarioModel);
        return funcionarioMapper.toDTO(funcionarioSalvo);
    }
}
