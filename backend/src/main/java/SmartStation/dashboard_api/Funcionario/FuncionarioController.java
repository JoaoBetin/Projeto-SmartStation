package SmartStation.dashboard_api.Funcionario;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

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

    @GetMapping("/listarID/{id}")
    public ResponseEntity<?> listarID(@RequestBody Long id){
        FuncionarioDTO funcionarioDTO = funcionarioService.listarFuncionariosID(id);

        if(funcionarioDTO != null){
            return ResponseEntity.status(HttpStatus.FOUND)
                    .body(funcionarioDTO);
        }
        return ResponseEntity.status(HttpStatus.NOT_FOUND)
                .body("Funcionario nao encontrado");
    }

    @DeleteMapping("/deletar/{id}")
    public ResponseEntity<?> deletarFuncionario(@RequestBody Long id){
        FuncionarioDTO funcionarioDTO = funcionarioService.listarFuncionariosID(id);

        if(funcionarioDTO != null){
            funcionarioService.deletarFuncionario(id);
            return ResponseEntity.ok(id + " foi deletado");
        }

        return ResponseEntity.status(HttpStatus.NOT_FOUND)
                .body(id + " nao foi encontrado");
    }
}
