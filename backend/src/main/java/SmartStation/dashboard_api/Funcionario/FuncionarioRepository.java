package SmartStation.dashboard_api.Funcionario;

import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface FuncionarioRepository extends JpaRepository<FuncionarioModel, Long> {
    List<FuncionarioModel> findDistinctBySessaoModelsAtivaTrue();
}
