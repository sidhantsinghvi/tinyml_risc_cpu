module cpu_top (
    input  clk,
    input  rst,
    output [31:0] pc_value,
    output        parity_error
);
    wire [31:0] instruction;
    wire [3:0]  opcode;
    wire [3:0]  rd;
    wire [3:0]  rs1;
    wire [3:0]  rs2;
    wire [15:0] imm16;

    wire        reg_write;
    wire        alu_src_imm;
    wire [3:0]  alu_ctrl;
    wire [1:0]  writeback_sel;

    wire [31:0] rs1_data;
    wire [31:0] rs2_data;
    wire [31:0] alu_operand_b;
    wire [31:0] alu_result;
    wire [31:0] imm_ext;
    wire [31:0] imm_low;
    wire [31:0] imm_high_merge;
    reg  [31:0] write_back_data;

    pc pc_i (
        .clk    (clk),
        .rst    (rst),
        .pc_out (pc_value)
    );

    instruction_memory imem_i (
        .pc         (pc_value),
        .instruction(instruction)
    );

    decoder decoder_i (
        .instruction(instruction),
        .opcode     (opcode),
        .rd         (rd),
        .rs1        (rs1),
        .rs2        (rs2),
        .imm16      (imm16)
    );

    control_unit ctrl_i (
        .opcode       (opcode),
        .reg_write    (reg_write),
        .alu_src_imm  (alu_src_imm),
        .alu_op       (alu_ctrl),
        .writeback_sel(writeback_sel)
    );

    regfile regfile_i (
        .clk          (clk),
        .rst          (rst),
        .we           (reg_write),
        .rs1          (rs1),
        .rs2          (rs2),
        .rd           (rd),
        .wd           (write_back_data),
        .rd1          (rs1_data),
        .rd2          (rs2_data),
        .parity_error (parity_error)
    );

    assign imm_ext        = {{16{imm16[15]}}, imm16};
    assign imm_low        = {16'h0000, imm16};
    assign imm_high_merge = {imm16, rs1_data[15:0]};

    assign alu_operand_b = alu_src_imm ? imm_ext : rs2_data;

    alu alu_i (
        .a      (rs1_data),
        .b      (alu_operand_b),
        .opcode (alu_ctrl),
        .result (alu_result)
    );

    always @(*) begin
        case (writeback_sel)
            2'b00: write_back_data = alu_result;
            2'b01: write_back_data = imm_low;
            2'b10: write_back_data = imm_high_merge;
            default: write_back_data = alu_result;
        endcase
    end
endmodule
