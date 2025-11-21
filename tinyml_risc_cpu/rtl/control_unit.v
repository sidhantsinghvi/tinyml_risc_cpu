module control_unit (
    input  [3:0] opcode,
    output reg       reg_write,
    output reg       alu_src_imm,
    output reg [3:0] alu_op,
    output reg [1:0] writeback_sel
);
    localparam WB_ALU      = 2'b00;
    localparam WB_IMM_LOW  = 2'b01;
    localparam WB_IMM_HIGH = 2'b10;

    always @(*) begin
        reg_write     = 1'b0;
        alu_src_imm   = 1'b0;
        alu_op        = opcode;
        writeback_sel = WB_ALU;

        case (opcode)
            4'b0000, // add
            4'b0001, // sub
            4'b0010, // and
            4'b0011, // or
            4'b0100, // xor
            4'b1000: begin // mac4
                reg_write     = 1'b1;
                writeback_sel = WB_ALU;
            end
            4'b0101: begin // load immediate low half
                reg_write     = 1'b1;
                writeback_sel = WB_IMM_LOW;
            end
            4'b0110: begin // load immediate high half
                reg_write     = 1'b1;
                writeback_sel = WB_IMM_HIGH;
            end
            default: begin
                reg_write     = 1'b0;
                writeback_sel = WB_ALU;
            end
        endcase
    end
endmodule
