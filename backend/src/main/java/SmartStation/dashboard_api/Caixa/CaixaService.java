package SmartStation.dashboard_api.Caixa;

import SmartStation.dashboard_api.Sessao.SessaoModel;
import SmartStation.dashboard_api.Sessao.SessaoRepository;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

@Service
public class CaixaService {

    private final CaixaMapper caixaMapper;
    private final CaixaRepository caixaRepository;
    private final SessaoRepository sessaoRepository;

    public CaixaService(CaixaMapper caixaMapper, CaixaRepository caixaRepository, SessaoRepository sessaoRepository) {
        this.caixaMapper = caixaMapper;
        this.caixaRepository = caixaRepository;
        this.sessaoRepository = sessaoRepository;
    }

    // Listar todas
    public List<CaixaDTO> listarCaixas(){
        List<CaixaModel> lista = caixaRepository.findAll();

        return lista.stream()
                .map(caixaMapper::toDTO)
                .collect(Collectors.toList());
    }

    // Listar por ID
    public CaixaDTO listarCaixaID(Long id){
        Optional<CaixaModel> caixa = caixaRepository.findById(id);

        return caixa.map(caixaMapper::toDTO).orElse(null);
    }

    // Criar
    public CaixaDTO criarCaixa(CaixaDTO dto){

        CaixaModel model = caixaMapper.toEntity(dto);

        CaixaModel salva = caixaRepository.save(model);

        return caixaMapper.toDTO(salva);
    }

    // Caixa Detectada
    public CaixaDTO registrarDeteccao(CaixaDTO dto){

        CaixaModel caixaModel = caixaMapper.toEntity(dto);

        SessaoModel sessao = sessaoRepository.findById(dto.getSessaoId())
                .orElseThrow(() -> new RuntimeException("Sessao nao encontrada"));

        caixaModel.setSessaoModel(sessao);

        if(caixaModel.getInicio_deteccao() != null && caixaModel.getFim_deteccao() != null){

            long tempo = java.time.Duration.between(
                    caixaModel.getInicio_deteccao(),
                    caixaModel.getFim_deteccao()
            ).getSeconds();

            caixaModel.setTempo_detectado(tempo);
        }

        CaixaModel caixaSalva = caixaRepository.save(caixaModel);

        Integer total = sessao.getTotalCaixas();

        if(total == null){
            total = 0;
        }

        sessao.setTotalCaixas(total + 1);

        sessaoRepository.save(sessao);

        return caixaMapper.toDTO(caixaSalva);
    }

    // Deletar
    public void deletarCaixa(Long id){
        caixaRepository.deleteById(id);
    }

    // Alterar
    public CaixaDTO alterarCaixa(Long id, CaixaDTO dto){

        CaixaModel model = caixaRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Caixa nao encontrada"));

        if(dto.getSessaoId() != null){

            SessaoModel sessao = sessaoRepository.findById(dto.getSessaoId())
                    .orElseThrow(() -> new RuntimeException("Sessao nao encontrada"));

            model.setSessaoModel(sessao);
        }

        if(dto.getInicio_deteccao() != null){
            model.setInicio_deteccao(dto.getInicio_deteccao());
        }

        if(dto.getFim_deteccao() != null){
            model.setFim_deteccao(dto.getFim_deteccao());
        }

        if(dto.getTempo_detectado() != null){
            model.setTempo_detectado(dto.getTempo_detectado());
        }

        CaixaModel salva = caixaRepository.save(model);

        return caixaMapper.toDTO(salva);
    }
}