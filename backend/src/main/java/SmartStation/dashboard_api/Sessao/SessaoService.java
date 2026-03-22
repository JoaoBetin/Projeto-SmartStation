package SmartStation.dashboard_api.Sessao;

import SmartStation.dashboard_api.Funcionario.FuncionarioModel;
import SmartStation.dashboard_api.Funcionario.FuncionarioRepository;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

@Service
public class SessaoService {
    SessaoMapper sessaoMapper;
    SessaoRepository sessaoRepository;
    FuncionarioRepository funcionarioRepository;

    public SessaoService(SessaoMapper sessaoMapper, SessaoRepository sessaoRepository, FuncionarioRepository funcionarioRepository) {
        this.sessaoMapper = sessaoMapper;
        this.sessaoRepository = sessaoRepository;
        this.funcionarioRepository = funcionarioRepository;
    }

    // Listar todos
    public List<SessaoDTO> listarSessao(){
        List<SessaoModel> sessaoModelList = sessaoRepository.findAll();

        return sessaoModelList.stream()
                .map(sessaoMapper::toDTO)
                .collect(Collectors.toList());
    }

    // Listar por ID
    public SessaoDTO listarSessaoID(Long id){
        Optional<SessaoModel> sessaoModelOptional = sessaoRepository.findById(id);

        return sessaoModelOptional.map(sessaoMapper::toDTO).orElse(null);
    }

    // Criar
    public SessaoDTO criarSessao(SessaoDTO sessaoDTO){

        SessaoModel sessaoModel = sessaoMapper.toEntity(sessaoDTO);

        SessaoModel sessaoSalva = sessaoRepository.save(sessaoModel);

        return sessaoMapper.toDTO(sessaoSalva);
    }

    // Deletar
    public void deletarSessao(Long id){
        sessaoRepository.deleteById(id);
    }

    // Alterar ID
    public SessaoDTO alterarSessao(Long id, SessaoDTO sessaoDTO){
        SessaoModel sessaoModel = sessaoRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Sessao nao encontrada"));

        if (sessaoDTO.getFuncionarioID() != null) {
            FuncionarioModel funcionario = funcionarioRepository.findById(sessaoDTO.getFuncionarioID())
                    .orElseThrow(() -> new RuntimeException("Funcionario nao encontrado: " + sessaoDTO.getFuncionarioID()));
            sessaoModel.setFuncionarioModel(funcionario);
        }

        if (sessaoDTO.getData() != null) sessaoModel.setData(sessaoDTO.getData());
        if (sessaoDTO.getAtiva() != null) sessaoModel.setAtiva(sessaoDTO.getAtiva());
        if (sessaoDTO.getHoraInicio() != null) sessaoModel.setHoraInicio(sessaoDTO.getHoraInicio());
        if (sessaoDTO.getHoraFim() != null) sessaoModel.setHoraFim(sessaoDTO.getHoraFim());
        if (sessaoDTO.getTempoOcioso() != null) sessaoModel.setTempoOcioso(sessaoDTO.getTempoOcioso());
        if (sessaoDTO.getTotalCaixas() != null) sessaoModel.setTotalCaixas(sessaoDTO.getTotalCaixas());

        return sessaoMapper.toDTO(sessaoRepository.save(sessaoModel));
    }
}

