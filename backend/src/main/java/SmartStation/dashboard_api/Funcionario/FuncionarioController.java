package SmartStation.dashboard_api.Funcionario;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/funcionario")
public class FuncionarioController {
    private final FuncionarioService funcionarioService;

    public FuncionarioController(FuncionarioService funcionarioService) {
        this.funcionarioService = funcionarioService;
    }

    @GetMapping("/listar")
    public ResponseEntity<?> listarTodos(){
        List<FuncionarioDTO> funcionarioDTOList = funcionarioService.listarFuncionarios();
        if(!funcionarioDTOList.isEmpty()){
            return ResponseEntity.status(HttpStatus.FOUND)
                    .body(funcionarioDTOList);
        }
        return ResponseEntity.status(HttpStatus.NOT_FOUND)
                .body("Nenhum funcionario registrado");
    }
}
