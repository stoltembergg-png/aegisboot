# OpenCore Continuous Fork — Prompt Pack

Objetivo do projeto:
manter um fork permanente do OpenCorePkg, sempre sincronizado com upstream, com CI/CD mais rigoroso, revisão automatizada, auto-merge seguro e releases próprias mais frequentes quando mudanças relevantes forem integradas.

Princípios:
- não reescrever OpenCore do zero;
- não divergir desnecessariamente;
- manter compatibilidade upstream;
- upstream continua sendo a principal base de código;
- toda mudança passa por gates técnicos;
- nenhum merge só porque "parece bom";
- nenhuma release sem validação;
- commits relevantes podem virar releases do fork sem esperar a próxima release oficial upstream;
- automação deve falhar de forma conservadora;
- releases devem ser rastreáveis ao SHA upstream e ao SHA do fork.

Ordem recomendada:
1. `01_PROJECT_SDD.md`
2. `02_UPSTREAM_SYNC_MODEL.md`
3. `03_REPOSITORY_BOOTSTRAP.md`
4. `04_CI_CD_SECURITY_BASELINE.md`
5. `05_WORKFLOW_INTEGRITY_GATES.md`
6. `06_BUILD_AND_REPRODUCIBILITY.md`
7. `07_DEEP_TEST_STRATEGY.md`
8. `08_QEMU_OVMF_BOOT_REGRESSION.md`
9. `09_PR_REVIEW_AUTOMATION.md`
10. `10_AUTOMERGE_POLICY.md`
11. `11_RELEASE_IMPACT_CLASSIFIER.md`
12. `12_RELEASE_PIPELINE.md`
13. `13_UPSTREAM_CONFLICT_RESOLUTION.md`
14. `14_PATCH_STACK_POLICY.md`
15. `15_DEPENDENCY_AND_SUPPLY_CHAIN.md`
16. `16_SECURITY_THREAT_MODEL.md`
17. `17_OBSERVABILITY_AND_HEALTH.md`
18. `18_AUTONOMOUS_MAINTENANCE_LOOP.md`
19. `19_INCIDENT_AND_ROLLBACK.md`
20. `20_RELEASE_CHANNELS.md`
21. `21_COMMUNITY_GOVERNANCE.md`
22. `22_DOCUMENTATION_AND_COMPATIBILITY.md`
23. `23_FINAL_AUTONOMY_AUDIT.md`
24. `24_MASTER_ORCHESTRATOR.md`
25. `25_INITIAL_PR_QUEUE.md`

Use cada prompt contra o estado real do repositório. Não presuma que uma etapa anterior foi concluída sem verificar arquivos, workflows, branch rules, checks e artefatos existentes.
